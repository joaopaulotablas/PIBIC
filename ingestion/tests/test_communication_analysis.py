from datetime import date, datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from bpc_ingestion.communication_analysis import (
    MAX_COMMUNICATIONS, MAX_TEXT_CHARS, MAX_TOTAL_CHARS, minimize_text, prepare_inputs, store_result,
    validate_prepared_source, validate_result,
)
from bpc_ingestion.database import make_engine
from bpc_ingestion.models import Base, ComunicacaoPje, ExtracaoIa, Processo


def _db():
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine


def _add_process(session, number, text="A decisão administrativa permaneceu sem análise."):
    process = Processo(numero_processo=number)
    session.add(process)
    session.flush()
    comm = ComunicacaoPje(
        processo_id=process.id, comunica_id=f"pub-{process.id}",
        hash_conteudo=f"{process.id:064x}", tribunal="TRF1",
        tipo_comunicacao="Comunicação", tipo_documento="Decisão",
        data_disponibilizacao=date(2026, 1, 1), texto=text, link=None,
        payload={}, coletado_em=datetime.now(timezone.utc),
    )
    session.add(comm)
    session.flush()
    return process, comm


def _result(source, cid=None, digest=None, passage=None):
    comm = source[0]["comunicacoes"][0]
    return {
        "resumo_caso": "A publicação relata demora administrativa.",
        "motivo_judicializacao": "demora_administrativa",
        "motivo_administrativo_negativa": "indeterminado",
        "resultado_judicial": "indeterminado",
        "evidencias": [{
            "comunicacao_id": cid if cid is not None else comm["comunicacao_id"],
            "hash_conteudo": digest if digest is not None else comm["hash_conteudo"],
            "trecho_sustentacao": passage if passage is not None else "permaneceu sem análise",
            "sustenta": "motivo_judicializacao",
        }],
        "lacunas": ["motivo administrativo da negativa não informado"],
    }


def test_evidence_requires_matching_communication_hash_and_passage():
    engine = _db()
    with Session(engine) as session:
        process, _ = _add_process(session, "0000001-00.2021.4.01.3400")
        source = prepare_inputs(session)
        validate_prepared_source(session, source[0])
        other, other_comm = _add_process(session, "0000002-00.2021.4.01.3400")
        with pytest.raises(ValueError, match="comunicação/hash"):
            validate_result(_result(source, digest="0" * 64), source)
        with pytest.raises(ValueError, match="comunicação/hash"):
            validate_result(_result(source, cid=other_comm.id, digest=other_comm.hash_conteudo), source)
        with pytest.raises(ValueError, match="trecho de evidência"):
            validate_result(_result(source, passage="trecho ausente"), source)
        altered = dict(source[0])
        altered["comunicacoes"] = [dict(source[0]["comunicacoes"][0], texto_minimizado="texto adulterado")]
        with pytest.raises(ValueError, match="nao corresponde"):
            validate_prepared_source(session, altered)
    engine.dispose()


def test_minimization_removes_parties_direct_identifiers_and_addresses():
    clean = minimize_text(
        "Capa com JOÃO DA SILVA. SENTENÇA. Impetrante: MARIA DE SOUZA. "
        "CPF 123.456.789-00, Rua das Flores, 123, telefone 61999999999. "
        "A análise administrativa não foi concluída."
    )
    for sensitive in ("JOÃO", "SILVA", "MARIA", "SOUZA", "123.456.789-00",
                      "Rua das Flores", "61999999999"):
        assert sensitive not in clean
    assert "análise administrativa" in clean


def test_input_limits_reject_instead_of_silent_truncation():
    engine = _db()
    with Session(engine) as session:
        for i in range(MAX_COMMUNICATIONS + 1):
            _add_process(session, f"00000{i+1}-00.2021.4.01.3400")
        with pytest.raises(ValueError, match="limit"):
            prepare_inputs(session, MAX_COMMUNICATIONS + 1)
        prepared = prepare_inputs(session, MAX_COMMUNICATIONS)
        assert sum(len(x["comunicacoes"]) for x in prepared) == MAX_COMMUNICATIONS
    engine.dispose()
    engine = _db()
    with Session(engine) as session:
        session.add(Processo(numero_processo="9999999-00.2021.4.01.3400"))
        session.flush()
        p = session.scalar(select(Processo).where(Processo.numero_processo.startswith("999")))
        session.add(ComunicacaoPje(
            processo_id=p.id, hash_conteudo="f" * 64, tipo_documento="Decisão",
            texto="x" * (MAX_TEXT_CHARS + 1), payload={}, coletado_em=datetime.now(timezone.utc),
        ))
        session.flush()
        with pytest.raises(ValueError, match="excede"):
            prepare_inputs(session, 20)
    engine.dispose()
    engine = _db()
    with Session(engine) as session:
        for i in range(4):
            _add_process(session, f"00000{i+1}-00.2021.4.01.3400", "a" * 16_000)
        with pytest.raises(ValueError, match=str(MAX_TOTAL_CHARS)):
            prepare_inputs(session, 20)
    engine.dispose()


def test_absent_evidence_is_rejected_for_claims_but_indeterminate_is_allowed():
    engine = _db()
    with Session(engine) as session:
        _add_process(session, "0000001-00.2021.4.01.3400")
        source = prepare_inputs(session)
        no_evidence = _result(source)
        no_evidence["evidencias"] = []
        no_evidence["resultado_judicial"] = "procedente"
        with pytest.raises(ValueError, match="sem evidência"):
            validate_result(no_evidence, source)
        indeterminate = _result(source)
        indeterminate["evidencias"] = []
        indeterminate["motivo_judicializacao"] = "indeterminado"
        indeterminate["motivo_administrativo_negativa"] = "indeterminado"
        indeterminate["resultado_judicial"] = "indeterminado"
        assert validate_result(indeterminate, source)["status_validacao"] == "pendente"
    engine.dispose()


def test_import_inserts_new_extraction_without_overwriting_existing():
    engine = _db()
    with Session(engine) as session:
        process, _ = _add_process(session, "0000001-00.2021.4.01.3400")
        old = ExtracaoIa(processo_id=process.id, tipo_extracao="triagem_bpc",
                         modelo="model-old", versao_prompt="v1",
                         resultado={"desfecho": "indeterminado"}, status_validacao="validada")
        session.add(old)
        session.flush()
        old_id = old.id
        source = prepare_inputs(session)
        result = validate_result(_result(source), source)
        store_result(session, process.id, result)
        session.flush()
        rows = list(session.scalars(select(ExtracaoIa).order_by(ExtracaoIa.id)))
        assert len(rows) == 2
        assert rows[0].id == old_id and rows[0].resultado == {"desfecho": "indeterminado"}
        assert rows[0].status_validacao == "validada"
        assert rows[1].tipo_extracao == "comunicacao_bpc_texto"
        assert rows[1].status_validacao == "pendente"
    engine.dispose()


@pytest.mark.parametrize("operative", ["JULGO IMPROCEDENTE", "JULGO PROCEDENTE",
                                      "JULGO PARCIALMENTE PROCEDENTE", "EXTINGO"])
def test_minimization_preserves_operative_language(operative):
    clean = minimize_text(f"SENTENÇA\n{operative} o pedido de benefício assistencial.")
    assert operative in clean
    assert "SENTENÇA" in clean
    assert "benefício assistencial" in clean


@pytest.mark.parametrize("field,value", [("resumo_caso", ""), ("resumo_caso", " "),
                                       ("resumo_caso", "x" * 1501),
                                       ("lacunas", 42), ("lacunas", [""]),
                                       ("lacunas", [False])])
def test_result_rejects_invalid_summary_and_gaps(field, value):
    result = {"resumo_caso": "Não há elementos suficientes.",
              "motivo_judicializacao": "indeterminado",
              "motivo_administrativo_negativa": "indeterminado",
              "resultado_judicial": "indeterminado", "evidencias": [], "lacunas": []}
    result[field] = value
    with pytest.raises(ValueError):
        validate_result(result, [])
