"""Reproducible local pilot commands. No external document transport is enabled."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path

from sqlalchemy.engine import URL
from sqlalchemy.orm import Session

from .database import make_engine
from .document_analysis import (
    ABSTENTION_SUMMARY, prepare_pilot, store_result,
    validate_prepared_source, validate_result,
)
from .document_schemas import (
    DOCUMENT_ANALYSIS_PROMPT, MAX_PILOT, PIPELINE_VERSION, PROMPT_VERSION,
    SCHEMA_VERSION, TYPE, DocumentResult,
)

ORIGINAL_DATABASE = Path("data/bpc-consolidado-luna-20261007.sqlite")


def backup_database(original: Path, destination: Path) -> dict:
    """SQLite backup from read-only source into an exclusively reserved NEW file."""
    if not original.is_file() or original.resolve() == destination.resolve():
        raise ValueError("backup_exige_origem_existente_e_destino_novo")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb"):
        pass
    with sqlite3.connect(original.resolve().as_uri() + "?mode=ro", uri=True) as source:
        with sqlite3.connect(destination) as target:
            source.backup(target)
            integrity = target.execute("PRAGMA integrity_check").fetchone()[0]
            foreign_keys = target.execute("PRAGMA foreign_key_check").fetchall()
    if integrity != "ok" or foreign_keys:
        raise ValueError("backup_falhou_integridade_ou_fk")
    return dict(integrity_check=integrity, violacoes_fk=len(foreign_keys))


def write_new_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as output:
        json.dump(data, output, ensure_ascii=False, indent=2)
        output.write("\n")


def prepare_command(args: argparse.Namespace) -> int:
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8-sig"))
    entries = manifest.get("processos") if isinstance(manifest, dict) else None
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_PILOT:
        raise ValueError("use_manifesto_explicito_do_piloto_de_1_a_40_nao_o_manifesto_200")
    if args.output.exists() or args.report.exists():
        raise FileExistsError("saida_e_relatorio_precisam_ser_novos")
    bronze_map = {}
    if getattr(args, "bronze_map", None):
        mapping = json.loads(args.bronze_map.read_text(encoding="utf-8-sig"))
        for item in mapping["documentos"]:
            candidates = item["candidatos_hash_validado"]
            if (type(item["documento_id"]) is not int or len(candidates) != 1
                    or not isinstance(candidates[0], str) or item["documento_id"] in bronze_map):
                raise ValueError("mapeamento_bronze_exige_um_caminho_explicito_por_documento")
            bronze_map[item["documento_id"]] = candidates[0]
    quality = backup_database(args.database, args.backup)
    engine = make_engine(URL.create("sqlite", database=str(args.backup.resolve())))
    try:
        with Session(engine) as session:
            queue = prepare_pilot(session, entries, args.raw_root, bronze_map)
    finally:
        engine.dispose()
    queue.update(database_backup=str(args.backup.resolve()),
                 mapeamento_bronze=str(args.bronze_map.resolve()) if getattr(args, "bronze_map", None) else None,
                 manifesto=str(args.manifest.resolve()),
                 sha256_manifesto=hashlib.sha256(manifest_bytes).hexdigest(),
                 prompt=DOCUMENT_ANALYSIS_PROMPT, schema=DocumentResult.model_json_schema(),
                 resumo_abstencao=ABSTENTION_SUMMARY)
    write_new_json(args.output, queue)
    report = dict(
        tipo_extracao=TYPE, versao_prompt=PROMPT_VERSION, versao_schema=SCHEMA_VERSION,
        versao_pipeline=PIPELINE_VERSION, manifesto=queue["manifesto"],
        sha256_manifesto=queue["sha256_manifesto"], banco_origem=str(args.database.resolve()),
        copia_nova=queue["database_backup"], fila=str(args.output.resolve()),
        selecionados=queue["selecionados"], preparados=len(queue["processos"]),
        documentos_preparados=sum(len(x["documentos"]) for x in queue["processos"]),
        caracteres_preparados=sum(x["caracteres"] for x in queue["processos"]),
        mapeamento_bronze=queue["mapeamento_bronze"], documentos_remapeados=len(bronze_map),
        bloqueados=queue["bloqueados"],
        motivos_bloqueio=dict(Counter(x["motivo"] for x in queue["bloqueados"])),
        chamadas_externas_executadas=0, extracoes_persistidas=0,
        revisao_humana="pendente", revisao_privacidade="pendente",
        envio_externo_permitido=False, **quality,
    )
    write_new_json(args.report, report)
    print(json.dumps({k: report[k] for k in (
        "selecionados", "preparados", "documentos_preparados", "motivos_bloqueio",
        "chamadas_externas_executadas", "extracoes_persistidas", "integrity_check", "violacoes_fk",
    )}, ensure_ascii=False))
    return 0


def import_command(args: argparse.Namespace) -> int:
    if not isinstance(args.model, str) or not args.model.strip() or len(args.model) > 100:
        raise ValueError("modelo_real_obrigatorio_ate_100_caracteres")
    if (not args.database.is_file() or args.database.resolve() == ORIGINAL_DATABASE.resolve()
            or (ORIGINAL_DATABASE.exists() and args.database.samefile(ORIGINAL_DATABASE))):
        raise ValueError("importacao_exige_copia_SQLite_nunca_banco_original")
    prepared = json.loads(args.source.read_text(encoding="utf-8-sig"))
    results = json.loads(args.results.read_text(encoding="utf-8-sig"))
    if (not isinstance(prepared, dict) or prepared.get("tipo_extracao") != TYPE
            or prepared.get("versao_prompt") != PROMPT_VERSION
            or prepared.get("versao_schema") != SCHEMA_VERSION
            or prepared.get("versao_pipeline") != PIPELINE_VERSION
            or not isinstance(prepared.get("processos"), list)
            or not isinstance(results, list) or not 1 <= len(results) <= MAX_PILOT):
        raise ValueError("fila_ou_resultados_fora_do_contrato_documental")
    sources = prepared["processos"]
    if not 1 <= len(sources) <= MAX_PILOT:
        raise ValueError("piloto_exige_1_a_40_entradas")
    by_id = {s["processo_id"]: s for s in sources}
    if len(by_id) != len(sources):
        raise ValueError("entrada_preparada_duplicada")
    seen = set()
    engine = make_engine(URL.create("sqlite", database=str(args.database.resolve())))
    try:
        with Session(engine) as session, session.begin():
            for entry in results:
                pid = entry.get("processo_id") if isinstance(entry, dict) else None
                if type(pid) is not int or pid not in by_id or pid in seen:
                    raise ValueError("resultado_fora_da_fila_ou_duplicado")
                seen.add(pid)
                source = by_id[pid]
                validate_prepared_source(session, source, args.raw_root)
                result = validate_result(entry.get("resultado"), source)
                if args.executar_local:
                    store_result(session, source, result, args.model, args.raw_root)
    finally:
        engine.dispose()
    print(json.dumps(dict(resultados_validados=len(seen),
                          modo="importacao_local" if args.executar_local else "dry_run_local",
                          chamadas_externas_executadas=0, revisao_humana="pendente")))
    return 0


def add_prepare_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--database", type=Path, default=ORIGINAL_DATABASE)
    parser.add_argument("--backup", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, default=Path("data"))
    parser.add_argument("--bronze-map", type=Path, help="Auditoria local com um caminho alternativo por documento; todos os hashes são reconferidos")


def add_import_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--model", required=True, help="Modelo declarado realmente usado; importação não comprova chamada API")
    parser.add_argument("--raw-root", type=Path, default=Path("data"))
    parser.add_argument("--executar-local", action="store_true", help="Grava localmente, sempre pendente; sem opção é dry-run")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    add_prepare_arguments(commands.add_parser("preparar"))
    add_import_arguments(commands.add_parser("importar"))
    args = parser.parse_args()
    return prepare_command(args) if args.command == "preparar" else import_command(args)


if __name__ == "__main__":
    raise SystemExit(main())
