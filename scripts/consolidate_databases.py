"""Consolidate the application's analytical databases into a new SQLite file.

This is intentionally additive: inputs are read only and an existing output is
never overwritten. See docs/CONTRATOS.md for identity and conflict policy.
"""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import tempfile
import uuid
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import MetaData, func, inspect, select, text
from sqlalchemy.engine import URL
from sqlalchemy.sql.sqltypes import Uuid

from bpc_ingestion.database import make_engine
from bpc_ingestion.models import Base
from bpc_ingestion.portable import SQLITE_VIEWS


IDENTITIES = {
    "coletas": ("id",), "tarefas_painel": ("id",),
    "processos": ("numero_processo",),
    "registros_datajud": ("datajud_index", "datajud_id"),
    "recursos_externos": ("fonte", "recurso_id"), "assuntos": ("codigo",),
    "referencias_tpu": ("tipo", "codigo"),
    "registro_assuntos": ("registro_id", "assunto_codigo"),
    "coleta_registros_datajud": ("coleta_id", "registro_id"),
    "movimentos": ("registro_id", "sequencia"),
    "consultas_pje": ("processo_id",),
    "comunicacoes_pje": ("processo_id", "hash_conteudo"),
    "documento_chunks": ("comunicacao_id", "numero_chunk", "modelo_embedding", "versao_pipeline"),
    "extracoes_ia": ("processo_id", "tipo_extracao", "modelo", "versao_prompt"),
    "documentos_publicos": ("fonte", "documento_id", "hash_conteudo"),
    "documento_processos": ("documento_id", "processo_id"),
    "indicadores_bpc_municipio": ("fonte", "mes_ano", "codigo_ibge", "tipo_id"),
    "indicadores_inss_indeferimentos": ("fonte", "competencia", "uf", "especie", "motivo", "hash_arquivo"),
    "indicadores_inss_concessoes": ("fonte", "competencia", "uf", "especie", "codigo_despacho", "despacho", "hash_arquivo"),
}

SURROGATE_ID_TABLES = {
    "processos", "registros_datajud", "recursos_externos", "indicadores_bpc_municipio",
    "movimentos", "comunicacoes_pje", "documento_chunks", "extracoes_ia",
    "documentos_publicos", "indicadores_inss_indeferimentos", "indicadores_inss_concessoes",
}


def norm(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, bytes):
        return {"bytes_sha256": __import__("hashlib").sha256(value).hexdigest()}
    if isinstance(value, dict):
        return {str(k): norm(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [norm(v) for v in value]
    return value


def signature(row: dict[str, Any]) -> str:
    return json.dumps(norm(row), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def open_sqlite_gzip(path: Path, temp_dir: Path):
    if path.suffix != ".gz":
        return make_engine(URL.create("sqlite", database=str(path.resolve()))), None
    unpacked = temp_dir / (path.stem + ".sqlite")
    with gzip.open(path, "rb") as src, unpacked.open("wb") as dst:
        shutil.copyfileobj(src, dst)
    return make_engine(URL.create("sqlite", database=str(unpacked.resolve()))), unpacked


def natural_key(table, row):
    fields = IDENTITIES.get(table.name)
    if not fields:
        return None
    return tuple(norm(row.get(field)) for field in fields)


def remap_extraction_evidence(row, source_name, source_pk, mappings, dst, audit):
    """Translate declared JSON references, using only the same source's map."""
    result = row.get("resultado")
    if not isinstance(result, dict) or "evidencias" not in result:
        return
    result = deepcopy(result)
    evidence_list = result["evidencias"]
    if not isinstance(evidence_list, list):
        raise ValueError(f"{source_name}: extração {source_pk} com evidencias inválidas")
    for position, evidence in enumerate(evidence_list):
        if not isinstance(evidence, dict):
            raise ValueError(f"{source_name}: extração {source_pk} com evidência inválida")
        if "registro_id" not in evidence:
            continue
        original = evidence["registro_id"]
        mapped = mappings.get((source_name, "registros_datajud", original)) if type(original) is int else None
        if mapped is None:
            raise ValueError(f"{source_name}: extração {source_pk}, evidencias[{position}].registro_id "
                             "não identifica um registro inteiro da mesma origem")
        record = Base.metadata.tables["registros_datajud"]
        process_id = dst.execute(select(record.c.processo_id).where(record.c.id == mapped)).scalar_one()
        if process_id != row["processo_id"]:
            raise ValueError(f"{source_name}: extração {source_pk}, evidencias[{position}].registro_id "
                             "pertence a outro processo")
        evidence["registro_id"] = mapped
        audit.append({"source": source_name, "source_extraction_pk": norm(source_pk),
                      "evidence_position": position, "source_registro_id": original,
                      "target_registro_id": mapped})
    row["resultado"] = result
    for position, evidence in enumerate(evidence_list):
        if "comunicacao_id" not in evidence:
            continue
        original = evidence["comunicacao_id"]
        mapped = mappings.get((source_name, "comunicacoes_pje", original)) if type(original) is int else None
        if mapped is None:
            raise ValueError(f"{source_name}: evidencias[{position}].comunicacao_id inválido")
        table = Base.metadata.tables["comunicacoes_pje"]
        communication = dst.execute(select(table.c.processo_id, table.c.hash_conteudo)
                                    .where(table.c.id == mapped)).one()
        if communication.processo_id != row["processo_id"] or communication.hash_conteudo != evidence.get("hash_conteudo"):
            raise ValueError(f"{source_name}: evidencias[{position}].comunicacao_id com processo/hash divergente")
        evidence["comunicacao_id"] = mapped
        audit.append({"source": source_name, "source_extraction_pk": norm(source_pk),
                      "evidence_position": position, "source_comunicacao_id": original,
                      "target_comunicacao_id": mapped})


def merge(inputs: list[tuple[str, Any]], output: Path, report_path: Path, dry_run: bool = False):
    if output.exists() and not dry_run:
        raise FileExistsError(f"Saída já existe e foi preservada: {output}")
    if not inputs:
        raise ValueError("Nenhuma origem disponível")
    counts = Counter()
    conflicts: list[dict[str, Any]] = []
    evidence_remappings: list[dict[str, Any]] = []
    mappings: dict[tuple[str, str, Any], Any] = {}
    origin_by_identity: dict[tuple[str, Any], str] = {}
    target = make_engine(URL.create("sqlite", database=":memory:" if dry_run else str(output.resolve())))
    try:
        Base.metadata.create_all(target)
        # JSON evidence IDs are dependencies not expressed as SQL foreign keys.
        ordered_tables = [t for t in Base.metadata.sorted_tables if t.name != "extracoes_ia"]
        ordered_tables.append(Base.metadata.tables["extracoes_ia"])
        dst_tables = {t.name: t for t in ordered_tables}
        with target.begin() as dst, ExitStack() as source_connections:
            for source_name, source in inputs:
                src_names = set(inspect(source).get_table_names())
                unknown = src_names - set(dst_tables) - {"alembic_version"}
                if unknown:
                    raise ValueError(f"Tabelas fora do contrato em {source_name}: {sorted(unknown)}")
                source_conn = source_connections.enter_context(source.connect())
                if ("revisoes_caso" in src_names and source_conn.scalar(
                        select(func.count()).select_from(Base.metadata.tables["revisoes_caso"]))):
                    raise ValueError("Revisões humanas exigem remapeamento documental antes da união; use exportação portátil de uma única base para preservá-las.")
                for table_name, table in dst_tables.items():
                    if table_name not in src_names:
                        continue
                    source_table = MetaData().tables.get(table_name)
                    if source_table is None:
                        source_table = table.to_metadata(MetaData())
                    existing_rows = [dict(r) for r in dst.execute(select(table)).mappings()]
                    key_to_row = {natural_key(table, r): r for r in existing_rows if natural_key(table, r) is not None}
                    pk_cols = list(table.primary_key.columns)
                    existing_pk = {tuple(r[c.name] for c in pk_cols): r for r in existing_rows}
                    rows = source_conn.execute(select(source_table)).mappings()
                    batch = []
                    for source_row in rows:
                        row = dict(source_row)
                        src_pk = tuple(row[c.name] for c in pk_cols)
                        # All declared FKs are translated through the already-built parent maps.
                        for fk in table.foreign_keys:
                            target_col = fk.column
                            value = row.get(fk.parent.name)
                            mapped = mappings.get((source_name, target_col.table.name, value))
                            if mapped is None and value is not None:
                                # A parent with a stable non-surrogate identity maps to itself.
                                parent = dst_tables[target_col.table.name]
                                parent_row = dst.execute(select(parent).where(target_col == value)).mappings().first()
                                mapped = parent_row[target_col.name] if parent_row else None
                            if mapped is None and value is not None:
                                conflicts.append({"kind": "missing_parent", "source": source_name, "table": table_name,
                                                  "source_pk": norm(src_pk), "foreign_key": fk.parent.name})
                            elif mapped is not None:
                                row[fk.parent.name] = mapped
                        if table_name == "extracoes_ia":
                            remap_extraction_evidence(row, source_name, src_pk, mappings, dst, evidence_remappings)
                        key = natural_key(table, row)
                        matched = key_to_row.get(key) if key is not None else None
                        if matched is not None:
                            mapped_pk = tuple(matched[c.name] for c in pk_cols)
                            mappings[(source_name, table_name, src_pk[0] if len(src_pk) == 1 else src_pk)] = mapped_pk[0] if len(mapped_pk) == 1 else mapped_pk
                            comparable = {k: v for k, v in row.items() if k not in {c.name for c in pk_cols}}
                            kept = {k: v for k, v in matched.items() if k not in {c.name for c in pk_cols}}
                            if signature(comparable) == signature(kept):
                                counts[(source_name, table_name, "duplicate_identical")] += 1
                            else:
                                counts[(source_name, table_name, "conflict")] += 1
                                conflicts.append({"kind": "identity_content_conflict", "source": source_name, "table": table_name,
                                                  "source_identity": norm(key), "source_pk": norm(src_pk),
                                                  "kept_pk": norm(mapped_pk),
                                                  "kept_source": origin_by_identity.get((table_name, key), "origem anterior sem registro de origem")})
                            continue
                        # A numeric local ID is never used to identify an entity across sources.
                        for col in pk_cols:
                            try:
                                generated_integer = col.type.python_type is int
                            except (AttributeError, NotImplementedError):
                                generated_integer = False
                            if (generated_integer and table_name in SURROGATE_ID_TABLES and col.name == "id"
                                    and len(pk_cols) == 1 and not col.foreign_keys):
                                row.pop(col.name, None)
                        if table_name == "movimentos":
                            batch.append(row)
                            if len(batch) >= 2000:
                                dst.execute(table.insert(), batch)
                                batch.clear()
                            if key is not None:
                                key_to_row[key] = row
                                origin_by_identity[(table_name, key)] = source_name
                            counts[(source_name, table_name, "inserted")] += 1
                            continue
                        inserted = dst.execute(table.insert().values(**row))
                        if len(pk_cols) == 1:
                            dst_pk = inserted.inserted_primary_key[0]
                        else:
                            dst_pk = tuple(row[c.name] for c in pk_cols)
                        src_map_key = src_pk[0] if len(src_pk) == 1 else src_pk
                        mappings[(source_name, table_name, src_map_key)] = dst_pk
                        if key is not None:
                            key_to_row[key] = {**row, **{c.name: dst_pk if c is pk_cols[0] and len(pk_cols) == 1 else row.get(c.name) for c in pk_cols}}
                            origin_by_identity[(table_name, key)] = source_name
                        counts[(source_name, table_name, "inserted")] += 1
                    if batch:
                        dst.execute(table.insert(), batch)
        if not dry_run:
            with target.begin() as dst:
                for name, sql in SQLITE_VIEWS.items():
                    dst.execute(text(f"CREATE VIEW {name} AS {sql}"))
            with target.connect() as conn:
                fk_errors = conn.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
                integrity = conn.exec_driver_sql("PRAGMA integrity_check").scalar()
                if fk_errors or integrity != "ok":
                    raise RuntimeError(f"Validação SQLite falhou: integrity={integrity}; FK={len(fk_errors)}")
            report_path.write_text(json.dumps({"counts": {"|".join(k): v for k, v in counts.items()},
                                               "conflicts": conflicts,
                                               "evidence_remappings": evidence_remappings},
                                              ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return counts, conflicts
    finally:
        target.dispose()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="bpc-merge-") as td:
        temp = Path(td)
        inputs, engines = [], []
        for index, path in enumerate(args.sqlite):
            engine, unpacked = open_sqlite_gzip(path, temp)
            engines.append(engine)
            inputs.append((f"sqlite_{index + 1}:{path.name}", engine))
        try:
            counts, conflicts = merge(inputs, args.output, args.report, args.dry_run)
            print(json.dumps({"dry_run": args.dry_run, "tables": len({k[1] for k in counts}),
                              "conflicts": len(conflicts), "counts": {"|".join(k): v for k, v in counts.items()}},
                             ensure_ascii=False, indent=2))
        finally:
            for engine in engines:
                engine.dispose()


if __name__ == "__main__":
    main()
