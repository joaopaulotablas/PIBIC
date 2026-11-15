"""Entirely SYNTHETIC cases; no real judicial text or external model calls."""
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from bpc_ingestion import api
from bpc_ingestion.database import make_engine
from bpc_ingestion.document_analysis import (
    ABSTENTION_SUMMARY, payload_digest, prepare_pilot,
    prepare_process, store_result, validate_prepared_source, validate_result,
)
from bpc_ingestion.document_pipeline import backup_database, import_command, prepare_command
from bpc_ingestion.document_schemas import (
    MAX_CHARS, MAX_DOCUMENTS, MAX_PILOT, PROMPT_VERSION, TYPE,
)
from bpc_ingestion.models import Base, Coleta, DocumentoProcesso, DocumentoPublico, ExtracaoIa, Processo
from bpc_ingestion.pje_public import DOC_PATH, HOST, parse_document


@pytest.fixture
def db(tmp_path):
    engine = make_engine(f"sqlite:///{tmp_path / 'synthetic.sqlite'}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session, tmp_path
    engine.dispose()


def synthetic_case(session, root, index=1, narrative=None):
    number = f"{index:07d}-00.2026.4.01.0000"  # Explicitly synthetic, not valid CNJ checksum.
    docid = str(9000 + index)
    url = f"https://{HOST}{DOC_PATH}?ca=abcdef&idProcessoDoc={docid}"
    process = Processo(numero_processo=number)
    run = Coleta(id=uuid4(), fonte="fixture_sintetica", status="concluida", registros=1, parametros={})
    session.add_all([process, run])
    session.flush()
    if narrative is None:
        narrative = ("<p>CASO TOTALMENTE SINTÉTICO: foi alegada demora administrativa.</p>"
                     "<blockquote>No processo 9999999-00.2020.4.01.0000, JULGO PROCEDENTE.</blockquote>"
                     "<p>Ante o exposto, DEFIRO a tutela provisória para analisar o requerimento.</p>")
    body = (f"<meta charset='utf-8'><div class='folha'><p>PROCESSO: {number}</p>"
            f"{narrative}<p>ID do documento: {docid}</p></div>").encode()
    document = parse_document(body, number, docid, "Decisão", url)
    raw = root / f"fixture-sintetica-{index}.html.gz"
    with gzip.open(raw, "wb") as output:
        output.write(body)
    row = DocumentoPublico(**document, hash_conteudo=payload_digest(document["payload"]),
                           coleta_id=run.id, arquivo_bruto=str(raw),
                           coletado_em=datetime.now(timezone.utc))
    session.add(row)
    session.flush()
    session.add(DocumentoProcesso(documento_id=row.id, processo_id=process.id, criterio="cnj_explicito"))
    session.flush()
    entry = dict(processo_id=process.id, cnj=number, documentos=[dict(
        id=row.id, documento_id=docid, hash_conteudo=row.hash_conteudo)])
    return process, row, entry


def abstention():
    return dict(versao_prompt=PROMPT_VERSION, resumo_caso=ABSTENTION_SUMMARY,
                provavel_causa="indeterminado", ato_administrativo="indeterminado",
                negativa_administrativa="indeterminado", requisito_controvertido="indeterminado",
                fundamento_judicial="indeterminado", desfecho=dict(
                    resultado="indeterminado", natureza="indeterminado", transito_julgado="indeterminado"),
                evidencias=[], lacunas=["Exemplo sintético: faltam inicial e processo administrativo."],
                revisao_humana="pendente", status_validacao="pendente")


def evidence(source, passage, target):
    doc = source["documentos"][0]
    start = doc["texto"].index(passage)
    return dict(documento_id=doc["documento_id"], hash_conteudo=doc["hash_conteudo"],
                campo="texto", inicio=start, fim=start + len(passage), trecho=passage, sustenta=target)


def test_abstention_and_supported_provisional_outcome_never_become_final(db):
    session, root = db
    _, _, entry = synthetic_case(session, root)
    source = prepare_process(session, entry, root)
    result = abstention()
    assert validate_result(result, source) == result
    passage = "DEFIRO a tutela provisória para analisar o requerimento."
    result["desfecho"] = dict(resultado="ordem_processual", natureza="provisoria", transito_julgado="indeterminado")
    result["evidencias"] = [evidence(source, passage, "desfecho.resultado"),
                            evidence(source, passage, "desfecho.natureza")]
    assert validate_result(result, source)["desfecho"]["natureza"] == "provisoria"
    invalid_final = deepcopy(result)
    invalid_final["desfecho"]["natureza"] = "final"
    with pytest.raises(ValueError, match="provisoria_nao_prova_decisao_final"):
        validate_result(invalid_final, source)
    result["desfecho"]["transito_julgado"] = "sim"
    with pytest.raises(ValueError, match="transito_julgado_sem_evidencia"):
        validate_result(result, source)


def test_rejects_evidence_wrong_document_hash_exact_text_offsets_and_boolean(db):
    session, root = db
    _, _, entry = synthetic_case(session, root)
    _, other, _ = synthetic_case(session, root, 2)
    source = prepare_process(session, entry, root)
    original = evidence(source, "DEFIRO a tutela provisória", "desfecho.natureza")
    for changes in (dict(documento_id=other.id, hash_conteudo=other.hash_conteudo),
                    dict(hash_conteudo="0" * 64), dict(inicio=original["inicio"] + 1),
                    dict(fim=999999), dict(trecho="DEFIRO TUTELA"), dict(documento_id=True),
                    dict(inicio=True), dict(fim=-1), dict(campo="ementa")):
        result = dict(abstention(), evidencias=[dict(original, **changes)])
        with pytest.raises(ValueError):
            validate_result(result, source)


def test_rejects_real_quote_from_other_case_even_in_same_document(db):
    session, root = db
    _, _, entry = synthetic_case(session, root)
    source = prepare_process(session, entry, root)
    result = abstention()
    result["desfecho"]["resultado"] = "procedente"
    result["evidencias"] = [evidence(source, "JULGO PROCEDENTE", "desfecho.resultado")]
    with pytest.raises(ValueError, match="jurisprudencia_alheia"):
        validate_result(result, source)


def test_unmarked_foreign_precedent_region_rejected_and_operative_region_kept(db):
    session, root = db
    narrative = ("<p>Precedente citado:</p><p>JULGO PROCEDENTE no exemplo de outro caso.</p>"
                 "<p>Ante o exposto, INDEFIRO o pedido neste caso sintético.</p>")
    _, _, entry = synthetic_case(session, root, narrative=narrative)
    source = prepare_process(session, entry, root)
    with pytest.raises(ValueError, match="jurisprudencia_alheia"):
        validate_result(dict(abstention(), evidencias=[evidence(source, "JULGO PROCEDENTE", "desfecho.resultado")]), source)
    result = abstention()
    result["desfecho"]["resultado"] = "improcedente"
    result["evidencias"] = [evidence(source, "INDEFIRO o pedido", "desfecho.resultado")]
    validate_result(result, source)


@pytest.mark.parametrize("field", ["provavel_causa", "ato_administrativo", "negativa_administrativa",
                                        "requisito_controvertido", "fundamento_judicial"])
def test_model_ignoring_abstention_is_rejected_for_every_field(db, field):
    session, root = db
    _, _, entry = synthetic_case(session, root)
    source = prepare_process(session, entry, root)
    with pytest.raises(ValueError, match="sem_evidencia"):
        validate_result(dict(abstention(), **{field: "Fato inventado sem fonte"}), source)
    with pytest.raises(ValueError, match="resumo_caso_sem_evidencia"):
        validate_result(dict(abstention(), resumo_caso="O benefício foi concedido."), source)


def test_pending_review_only_unknown_keys_and_empty_gaps_rejected(db):
    session, root = db
    _, _, entry = synthetic_case(session, root)
    source = prepare_process(session, entry, root)
    for changes in (dict(status_validacao="revisado"), dict(revisao_humana=False),
                    dict(extra="unexpected"), dict(lacunas=[]), dict(lacunas=[" "]),
                    dict(versao_prompt="old")):
        with pytest.raises(ValueError):
            validate_result(dict(abstention(), **changes), source)


def test_explicit_process_link_and_frozen_hash_rechecked_against_database(db):
    session, root = db
    process, row, entry = synthetic_case(session, root)
    other, _, _ = synthetic_case(session, root, 2)
    with pytest.raises(ValueError, match="sem_vinculo"):
        prepare_process(session, dict(entry, processo_id=other.id, cnj=other.numero_processo), root)
    source = prepare_process(session, entry, root)
    altered = deepcopy(source)
    altered["documentos"][0]["texto"] += " texto adulterado"
    with pytest.raises(ValueError, match="entrada_preparada_diverge"):
        validate_prepared_source(session, altered, root)
    row.hash_conteudo = "0" * 64
    with pytest.raises(ValueError, match="hash_ou_identidade"):
        validate_prepared_source(session, source, root)
    assert session.scalar(select(func.count()).select_from(ExtracaoIa)) == 0


def test_supplementary_jurisprudence_cannot_enter_sample_even_when_linked(db):
    session, root = db
    _, row, entry = synthetic_case(session, root)
    row.fonte = "cjf_trf1"
    with pytest.raises(ValueError, match="nao_e_pje_proprio"):
        prepare_process(session, entry, root)


def test_missing_bronze_and_tampered_bronze_are_explicit_blocks(db):
    session, root = db
    _, row, entry = synthetic_case(session, root)
    raw = Path(row.arquivo_bruto)
    original = raw.read_bytes()
    row.arquivo_bruto = str(root / "missing.html.gz")
    queue = prepare_pilot(session, [entry], root)
    assert queue["processos"] == []
    assert queue["bloqueados"][0]["motivo"] == "bronze_ausente_ou_fora_da_raiz_local"
    row.arquivo_bruto = str(raw)
    with gzip.open(raw, "wb") as output:
        output.write(gzip.decompress(original).replace(b"tutela", b"outra"))
    with pytest.raises(ValueError, match="bronze_hash_divergente"):
        prepare_process(session, entry, root)


def test_explicit_local_bronze_map_recovers_historical_path_without_mutating_source(db):
    session, root = db
    _, row, entry = synthetic_case(session, root)
    original = row.arquivo_bruto
    row.arquivo_bruto = "old-machine/missing.html.gz"
    source = prepare_process(session, entry, root, {row.id: original})
    assert source["documentos"][0]["arquivo_bruto_original"] == "old-machine/missing.html.gz"
    assert source["documentos"][0]["arquivo_bruto_local"] == str(Path(original).resolve())
    assert row.arquivo_bruto == "old-machine/missing.html.gz"
    validate_prepared_source(session, source, root)
    with pytest.raises(ValueError, match="fora_da_raiz"):
        prepare_process(session, entry, root / "narrow-subdirectory", {row.id: original})
    _, other, _ = synthetic_case(session, root, 2)
    with pytest.raises(ValueError, match="bronze_identidade_documental_invalida"):
        prepare_process(session, entry, root, {row.id: other.arquivo_bruto})
    arbitrary = root / "arbitrary.html"
    arbitrary.write_text("SYNTHETIC arbitrary content", encoding="utf-8")
    with pytest.raises(ValueError, match="bronze_identidade_documental_invalida"):
        prepare_process(session, entry, root, {row.id: str(arbitrary)})


def test_limits_reject_without_truncating_documents_or_200_process_manifest(db):
    session, root = db
    _, _, entry = synthetic_case(session, root)
    with pytest.raises(ValueError, match="1_a_40"):
        prepare_pilot(session, [entry] * (MAX_PILOT + 1), root)
    with pytest.raises(ValueError, match="duplicado"):
        prepare_pilot(session, [entry, entry], root)
    with pytest.raises(ValueError, match="quantidade_documentos"):
        prepare_process(session, dict(entry, documentos=entry["documentos"] * (MAX_DOCUMENTS + 1)), root)
    _, _, long_entry = synthetic_case(session, root, 2, "<p>" + "x" * MAX_CHARS + "</p>")
    with pytest.raises(ValueError, match="sem_truncamento"):
        prepare_process(session, long_entry, root)


def test_store_validates_all_sources_records_provenance_and_is_append_only(db):
    session, root = db
    _, row, entry = synthetic_case(session, root)
    source = prepare_process(session, entry, root)
    output = abstention()
    first = store_result(session, source, output, "synthetic-local-fixture", root)
    assert first.status_validacao == "pendente"
    assert first.resultado["proveniencia"][0]["documento_id"] == row.id
    assert first.resultado["origem_execucao"] == "importacao_local"
    assert first.resultado["chamadas_externas_executadas"] == 0
    assert store_result(session, source, output, "synthetic-local-fixture", root).id == first.id
    with pytest.raises(ValueError, match="divergente_requer_nova_versao"):
        store_result(session, source, dict(output, lacunas=["Outra lacuna sintética"]), "synthetic-local-fixture", root)
    with pytest.raises(ValueError, match="externo_bloqueado"):
        store_result(session, source, output, "synthetic-local-fixture", root, origin="ipeaia_api")
    assert session.scalar(select(func.count()).select_from(ExtracaoIa)) == 1


def test_global_40_result_gate_prevents_rebatching_with_another_model(db):
    session, root = db
    process, _, entry = synthetic_case(session, root)
    source = prepare_process(session, entry, root)
    for n in range(MAX_PILOT):
        session.add(ExtracaoIa(processo_id=process.id, tipo_extracao=TYPE,
                    modelo=f"synthetic-{n}", versao_prompt="previous-version",
                    resultado={}, status_validacao="pendente"))
    session.flush()
    with pytest.raises(ValueError, match="gate_humano"):
        store_result(session, source, abstention(), "another-model", root)


def test_new_backup_preserves_source_and_refuses_overwrite(db):
    session, root = db
    synthetic_case(session, root)
    session.commit()
    original = root / "synthetic.sqlite"
    before = original.read_bytes()
    destination = root / "new.sqlite"
    assert backup_database(original, destination) == dict(integrity_check="ok", violacoes_fk=0)
    assert original.read_bytes() == before
    copied = destination.read_bytes()
    with pytest.raises(FileExistsError):
        backup_database(original, destination)
    assert destination.read_bytes() == copied


def test_api_default_retains_text_opt_in_requires_loopback_and_preserves_legacy(db):
    session, root = db
    process, row, entry = synthetic_case(session, root)
    source = prepare_process(session, entry, root)
    store_result(session, source, abstention(), "synthetic-local-fixture", root)
    session.add(ExtracaoIa(processo_id=process.id, tipo_extracao="triagem_bpc",
                modelo="legacy-fixture", versao_prompt="bpc_triagem_api_v1.0",
                resultado={"observacao_curta": "LEGADO SINTÉTICO"}, status_validacao="pendente"))
    session.commit()
    api.app.dependency_overrides[api.get_session] = lambda: session
    path = f"/admin/api/processos/{process.numero_processo}/analise-documental"
    try:
        client = TestClient(api.app)
        default = client.get(path)
        assert default.status_code == 200
        assert default.headers["cache-control"] == "no-store"
        assert default.json()["extracoes"][0]["resultado"] is None
        assert default.json()["documentos"][0]["texto"] is None
        assert client.get(path + "?incluir_texto_local=true").status_code == 403
        local_client = TestClient(api.app, base_url="http://127.0.0.1", client=("127.0.0.1", 10000))
        assert local_client.get(path + "?incluir_texto_local=true", headers={
            "Origin": "https://foreign.example"}).status_code == 403
        local = local_client.get(path + "?incluir_texto_local=true")
        assert local.status_code == 200
        assert local.json()["documentos"][0]["texto"] == row.texto
        assert local.json()["extracoes"][0]["status_validacao"] == "pendente"
        detail = client.get(f"/admin/api/processos/{process.numero_processo}").json()
        assert any(x["resultado"] == {"observacao_curta": "LEGADO SINTÉTICO"} for x in detail["extracoes_ia"])
        assert any(x["resultado"] is None for x in detail["extracoes_ia"])
        assert client.get("/admin/api/processos/invalid/analise-documental").status_code == 400
    finally:
        api.app.dependency_overrides.clear()


def test_api_without_extraction_does_not_invent_model_output(db):
    session, root = db
    process, _, _ = synthetic_case(session, root)
    session.commit()
    api.app.dependency_overrides[api.get_session] = lambda: session
    try:
        response = TestClient(api.app).get(f"/admin/api/processos/{process.numero_processo}/analise-documental")
        assert response.status_code == 200
        assert response.json()["extracoes"] == []
        assert any("Nenhuma extração" in x for x in response.json()["lacunas"])
    finally:
        api.app.dependency_overrides.clear()


def test_cli_dry_run_and_atomic_import_do_not_claim_model_calls(db):
    session, root = db
    _, _, entry = synthetic_case(session, root)
    session.commit()
    manifest = root / "pilot.json"
    manifest.write_text(json.dumps({"processos": [entry]}), encoding="utf-8")
    args = SimpleNamespace(manifest=manifest, database=root / "synthetic.sqlite",
        backup=root / "pilot-backup.sqlite", output=root / "queue.json",
        report=root / "report.json", raw_root=root)
    prepare_command(args)
    report = json.loads(args.report.read_text(encoding="utf-8"))
    assert report["preparados"] == 1
    assert report["chamadas_externas_executadas"] == 0
    results = root / "synthetic-results.json"
    results.write_text(json.dumps([dict(processo_id=entry["processo_id"], resultado=abstention())]), encoding="utf-8")
    imported = SimpleNamespace(database=args.backup, source=args.output, results=results,
                              model="synthetic-local-fixture", raw_root=root, executar_local=False)
    assert import_command(imported) == 0
    engine = make_engine(f"sqlite:///{args.backup}")
    with Session(engine) as check:
        assert check.scalar(select(func.count()).select_from(ExtracaoIa)) == 0
    imported.executar_local = True
    assert import_command(imported) == 0
    with Session(engine) as check:
        assert check.scalar(select(func.count()).select_from(ExtracaoIa)) == 1
    engine.dispose()


def test_import_rolls_back_entire_batch_when_later_result_is_invalid(db):
    session, root = db
    _, _, first = synthetic_case(session, root)
    _, _, second = synthetic_case(session, root, 2)
    session.commit()
    manifest = root / "pilot-atomic.json"
    manifest.write_text(json.dumps({"processos": [first, second]}), encoding="utf-8")
    args = SimpleNamespace(manifest=manifest, database=root / "synthetic.sqlite",
        backup=root / "atomic-backup.sqlite", output=root / "atomic-queue.json",
        report=root / "atomic-report.json", raw_root=root)
    prepare_command(args)
    results = root / "invalid-synthetic-results.json"
    results.write_text(json.dumps([
        dict(processo_id=first["processo_id"], resultado=abstention()),
        dict(processo_id=second["processo_id"], resultado=dict(abstention(), provavel_causa="Inventado")),
    ]), encoding="utf-8")
    imported = SimpleNamespace(database=args.backup, source=args.output, results=results,
                              model="synthetic-local-fixture", raw_root=root, executar_local=True)
    with pytest.raises(ValueError, match="sem_evidencia"):
        import_command(imported)
    engine = make_engine(f"sqlite:///{args.backup}")
    with Session(engine) as check:
        assert check.scalar(select(func.count()).select_from(ExtracaoIa)) == 0
    engine.dispose()
