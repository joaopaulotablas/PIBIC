from __future__ import annotations

from datetime import date, datetime, timezone
import uuid
import json

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.engine import URL

from bpc_ingestion.models import (
    Assunto, Base, Coleta, DocumentoProcesso, DocumentoPublico, ExtracaoIa, Processo,
    RegistroAssunto, ComunicacaoPje,
    RegistroDatajud, IndicadorBpcMunicipio,
)
from scripts.consolidate_databases import merge
from scripts.compare_consolidations import fingerprint


def db(path):
    engine = create_engine(URL.create("sqlite", database=str(path)))
    Base.metadata.create_all(engine)
    return engine


def seed(engine, process_id: int, number: str, *, doc_hash="a" * 64, doc_id="doc", quantity=10,
         record_id=1, result=None):
    run_id = uuid.uuid4()
    now = datetime(2026, 10, 7, tzinfo=timezone.utc)
    with engine.begin() as c:
        c.execute(Coleta.__table__.insert().values(id=run_id, fonte="test", status="concluida",
            parametros={}, registros=1, iniciado_em=now, finalizado_em=now))
        c.execute(Processo.__table__.insert().values(id=process_id, numero_processo=number,
            criado_em=now, atualizado_em=now))
        c.execute(RegistroDatajud.__table__.insert().values(id=record_id, processo_id=process_id,
            datajud_index="idx", datajud_id=f"hit-{number}", tribunal="TRF1", grau="G1",
            cursor_sort=[], payload={"cnj": number}, coletado_em=now))
        c.execute(Assunto.__table__.insert().values(codigo=11946, nome="Deficiente"))
        c.execute(RegistroAssunto.__table__.insert().values(registro_id=record_id, assunto_codigo=11946))
        c.execute(DocumentoPublico.__table__.insert().values(id=1, fonte="test", documento_id=doc_id,
            hash_conteudo=doc_hash, tipo_documento="decisao", tribunal="TRF1", numero_origem=number,
            numeros_cnj=[number], url_origem="https://example.test", recurso_url="https://example.test/doc",
            arquivo_bruto="missing.ndjson.gz", payload={"hash": doc_hash}, coleta_id=run_id,
            coletado_em=now))
        c.execute(DocumentoProcesso.__table__.insert().values(documento_id=1, processo_id=process_id,
            criterio="cnj_explicito"))
        c.execute(ExtracaoIa.__table__.insert().values(id=1, processo_id=process_id,
            tipo_extracao="resumo_caso", modelo="m", versao_prompt="v1",
            resultado=result if result is not None else {"x": 1},
            status_validacao="pendente", criado_em=now))
        c.execute(IndicadorBpcMunicipio.__table__.insert().values(id=1, fonte="portal_transparencia",
            mes_ano=202608, data_referencia=date(2026, 8, 31), codigo_ibge="5300108", tipo_id=1,
            quantidade_beneficiados=quantity, valor=100, payload={"q": quantity}, coleta_id=run_id,
            coletado_em=now))


def test_logical_ids_fk_remap_versions_and_extractions(tmp_path):
    a, b = db(tmp_path / "a.sqlite"), db(tmp_path / "b.sqlite")
    seed(a, 1, "0000001-00.2026.4.01.3400")
    # Same local integer IDs, different CNJ; one identical document and one new version.
    seed(b, 1, "0000002-00.2026.4.01.3400", doc_hash="b" * 64)
    with b.begin() as c:
        # Add a new version for the second process, sharing source document ID.
        c.execute(DocumentoPublico.__table__.insert().values(id=2, fonte="test", documento_id="doc",
            hash_conteudo="c" * 64, tipo_documento="decisao", tribunal="TRF1",
            numero_origem="0000002-00.2026.4.01.3400", numeros_cnj=["0000002-00.2026.4.01.3400"],
            url_origem="https://example.test", recurso_url="https://example.test/doc",
            arquivo_bruto="missing2.ndjson.gz", payload={"hash": "c" * 64},
            coleta_id=c.execute(select(Coleta.id)).scalar_one(), coletado_em=datetime(2026, 10, 7, tzinfo=timezone.utc)))
    out = tmp_path / "merged.sqlite"
    counts, _ = merge([("a", a), ("b", b)], out, tmp_path / "report.json")
    merged = create_engine(URL.create("sqlite", database=str(out)))
    with merged.connect() as c:
        processes = c.execute(select(Processo.numero_processo, Processo.id)).all()
        assert len(processes) == 2 and processes[0][1] != processes[1][1]
        assert c.execute(select(RegistroDatajud.id)).all().__len__() == 2
        assert c.execute(select(RegistroAssunto.assunto_codigo).distinct()).all() == [(11946,)]
        assert c.execute(select(DocumentoPublico.id)).all().__len__() == 3
        assert c.execute(select(DocumentoProcesso.processo_id)).all().__len__() == 2
        assert c.execute(select(ExtracaoIa.processo_id)).all().__len__() == 2
        indicators = c.execute(select(IndicadorBpcMunicipio.quantidade_beneficiados)).all()
        assert indicators == [(10,)]
        assert not c.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
    assert counts[("a", "processos", "inserted")] == 1
    merged.dispose(); a.dispose(); b.dispose()


def evidence_result(record_id):
    return {"evidencias": [{"registro_id": record_id, "campo": "classe",
                            "referencia": "Fato", "sustenta": "Classificação"}],
            "resumo_caso": "Resumo preservado", "metadata": {"registro_id": 999}}


@pytest.mark.parametrize("invalid", [None, "missing", "wrong_hash", "other_process", True])
def test_communication_evidence_remap(tmp_path, invalid):
    a, b = db(tmp_path / "a.sqlite"), db(tmp_path / "b.sqlite")
    for index, engine in enumerate((a, b), 1):
        number = f"000000{index}-00.2026.4.01.3400"
        seed(engine, 1, number)
        with engine.begin() as c:
            c.execute(ComunicacaoPje.__table__.insert().values(
                id=1, processo_id=1, hash_conteudo=str(index) * 64,
                texto="Texto", payload={}, coletado_em=datetime(2026, 10, 7)))
            result = {"evidencias": [{"comunicacao_id": 1, "hash_conteudo": str(index) * 64}]}
            if index == 2:
                if invalid == "missing": result["evidencias"][0]["comunicacao_id"] = 99
                if invalid == "wrong_hash": result["evidencias"][0]["hash_conteudo"] = "f" * 64
                if invalid is True: result["evidencias"][0]["comunicacao_id"] = True
                if invalid == "other_process":
                    c.execute(Processo.__table__.insert().values(id=2, numero_processo="0000003-00.2026.4.01.3400"))
                    c.execute(ComunicacaoPje.__table__.update().values(processo_id=2))
            c.execute(ExtracaoIa.__table__.update().values(resultado=result))
    output = tmp_path / "merged.sqlite"
    if invalid is not None:
        with pytest.raises(ValueError, match="comunicacao_id"):
            merge([("a", a), ("b", b)], output, tmp_path / "report.json")
    else:
        merge([("a", a), ("b", b)], output, tmp_path / "report.json")
        reverse = tmp_path / "reverse.sqlite"
        merge([("b", b), ("a", a)], reverse, tmp_path / "reverse.json")
        assert fingerprint(output)["extracoes_ia"] == fingerprint(reverse)["extracoes_ia"]
        merged = create_engine(URL.create("sqlite", database=str(output)))
        with merged.connect() as c:
            for pid, result in c.execute(select(ExtracaoIa.processo_id, ExtracaoIa.resultado)):
                cid = result["evidencias"][0]["comunicacao_id"]
                assert c.execute(select(ComunicacaoPje.processo_id).where(ComunicacaoPje.id == cid)).scalar_one() == pid
        merged.dispose()
    a.dispose(); b.dispose()


def test_evidence_remap_preserves_origin_and_logical_comparison(tmp_path):
    a, b = db(tmp_path / "a.sqlite"), db(tmp_path / "b.sqlite")
    seed(a, 1, "0000001-00.2026.4.01.3400", result=evidence_result(1))
    seed(b, 1, "0000002-00.2026.4.01.3400", doc_hash="b" * 64, result=evidence_result(1))
    out, reverse = tmp_path / "merged.sqlite", tmp_path / "reverse.sqlite"
    report = tmp_path / "report.json"
    merge([("a", a), ("b", b)], out, report)
    merge([("b", b), ("a", a)], reverse, tmp_path / "reverse.json")
    merged = create_engine(URL.create("sqlite", database=str(out)))
    with merged.connect() as c:
        for process_id, result in c.execute(select(ExtracaoIa.processo_id, ExtracaoIa.resultado)):
            actual = result["evidencias"][0]["registro_id"]
            expected = c.execute(select(RegistroDatajud.id).where(
                RegistroDatajud.processo_id == process_id)).scalar_one()
            assert actual == expected
            assert result == evidence_result(expected)
    with b.connect() as c:
        assert c.execute(select(ExtracaoIa.resultado)).scalar_one() == evidence_result(1)
    audit = json.loads(report.read_text(encoding="utf-8"))["evidence_remappings"]
    assert audit[-1] == {"source": "b", "source_extraction_pk": [1], "evidence_position": 0,
                         "source_registro_id": 1, "target_registro_id": 2}
    assert fingerprint(out)["extracoes_ia"] == fingerprint(reverse)["extracoes_ia"]
    merged.dispose(); a.dispose(); b.dispose()


def test_same_logical_extraction_deduplicates_after_evidence_remap(tmp_path):
    a, b = db(tmp_path / "a.sqlite"), db(tmp_path / "b.sqlite")
    number = "0000001-00.2026.4.01.3400"
    seed(a, 1, number, result=evidence_result(1))
    seed(b, 8, number, record_id=77, result=evidence_result(77))
    out = tmp_path / "merged.sqlite"
    counts, conflicts = merge([("a", a), ("b", b)], out, tmp_path / "report.json")
    assert counts[("b", "extracoes_ia", "duplicate_identical")] == 1
    assert not any(x["table"] == "extracoes_ia" for x in conflicts)
    merged = create_engine(URL.create("sqlite", database=str(out)))
    with merged.connect() as c:
        assert c.execute(select(ExtracaoIa.resultado)).scalar_one() == evidence_result(1)
    merged.dispose(); a.dispose(); b.dispose()


@pytest.mark.parametrize("reference", [1, 999, "1", True, None, "other_process"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_invalid_evidence_reference_rejects_merge(tmp_path, reference, dry_run):
    a, b = db(tmp_path / "a.sqlite"), db(tmp_path / "b.sqlite")
    # Destination ID 1 exists, but it must never resolve a missing source ID.
    seed(a, 1, "0000001-00.2026.4.01.3400")
    seed(b, 1, "0000002-00.2026.4.01.3400", doc_hash="b" * 64,
         record_id=77, result=evidence_result(2 if reference == "other_process" else reference))
    if reference == "other_process":
        with b.begin() as c:
            now = datetime(2026, 10, 7, tzinfo=timezone.utc)
            c.execute(Processo.__table__.insert().values(id=2, numero_processo="0000003-00.2026.4.01.3400",
                                                        criado_em=now, atualizado_em=now))
            c.execute(RegistroDatajud.__table__.insert().values(id=2, processo_id=2,
                datajud_index="idx", datajud_id="other", tribunal="TRF1", grau="G1",
                cursor_sort=[], payload={}, coletado_em=now))
    with pytest.raises(ValueError, match="registro_id"):
        merge([("a", a), ("b", b)], tmp_path / "out.sqlite", tmp_path / "report.json", dry_run)
    a.dispose(); b.dispose()


def test_duplicate_snapshot_is_not_summed_and_existing_output_refused(tmp_path):
    a, b = db(tmp_path / "a.sqlite"), db(tmp_path / "b.sqlite")
    seed(a, 1, "0000001-00.2026.4.01.3400")
    seed(b, 8, "0000001-00.2026.4.01.3400")
    out = tmp_path / "merged.sqlite"
    merge([("a", a), ("b", b)], out, tmp_path / "report.json")
    merged = create_engine(URL.create("sqlite", database=str(out)))
    with merged.connect() as c:
        assert c.execute(select(IndicadorBpcMunicipio.quantidade_beneficiados)).all() == [(10,)]
    with pytest.raises(FileExistsError):
        merge([("a", a)], out, tmp_path / "again.json")
    merged.dispose(); a.dispose(); b.dispose()
