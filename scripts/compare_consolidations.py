"""Compare two consolidations by logical identities and normalized row content."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.engine import URL

from bpc_ingestion.database import make_engine
from bpc_ingestion.models import Base
from scripts.consolidate_databases import IDENTITIES, SURROGATE_ID_TABLES, norm, signature


def freeze(value):
    if isinstance(value, dict):
        return tuple(sorted((key, freeze(item)) for key, item in value.items()))
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    return value


def fingerprint(path: Path):
    engine = make_engine(URL.create("sqlite", database=str(path.resolve())))
    try:
        identities = {}
        parents_needed = {fk.column.table.name for table in Base.metadata.tables.values()
                          for fk in table.foreign_keys}
        with engine.connect() as c:
            for table in Base.metadata.sorted_tables:
                if table.name not in parents_needed:
                    continue
                pks = list(table.primary_key.columns)
                selected = list(dict.fromkeys([x.name for x in pks] + list(IDENTITIES[table.name])))
                for row in c.execute(select(*(table.c[x] for x in selected))).mappings():
                    pk = tuple(row[x.name] for x in pks)
                    fields = IDENTITIES[table.name]
                    values = dict(row)
                    for fk in table.foreign_keys:
                        if fk.parent.name in fields and values[fk.parent.name] is not None:
                            values[fk.parent.name] = identities[(fk.column.table.name, (values[fk.parent.name],))]
                    identities[(table.name, pk)] = tuple(freeze(norm(values[name])) for name in fields)
            result = {}
            for table in Base.metadata.sorted_tables:
                pks = list(table.primary_key.columns)
                fk_by_column = {fk.parent.name: fk.column.table.name for fk in table.foreign_keys}
                current = Counter()
                for raw in c.execute(select(table).execution_options(stream_results=True)).mappings():
                    row = dict(raw)
                    if table.name == "extracoes_ia" and isinstance(row.get("resultado"), dict):
                        row["resultado"] = deepcopy(row["resultado"])
                        for evidence in row["resultado"].get("evidencias", []):
                            if "registro_id" in evidence:
                                evidence["registro_id"] = identities[("registros_datajud", (evidence["registro_id"],))]
                            if "comunicacao_id" in evidence:
                                evidence["comunicacao_id"] = identities[("comunicacoes_pje", (evidence["comunicacao_id"],))]
                    for fk_col, parent_table in fk_by_column.items():
                        value = row.get(fk_col)
                        if value is not None:
                            row[fk_col] = identities[(parent_table, (value,))]
                    for pk in pks:
                        try:
                            is_surrogate = pk.type.python_type is int
                        except (AttributeError, NotImplementedError):
                            is_surrogate = False
                        if is_surrogate and table.name in SURROGATE_ID_TABLES and pk.name == "id":
                            row.pop(pk.name, None)
                    identity = tuple(freeze(norm(row[name])) for name in IDENTITIES[table.name])
                    content = signature(row)
                    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
                    current[(identity, digest)] += 1
                result[table.name] = current
        return result
    finally:
        engine.dispose()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("left", type=Path)
    p.add_argument("right", type=Path)
    args = p.parse_args()
    left, right = fingerprint(args.left), fingerprint(args.right)
    mismatches = []
    for table in left:
        if left[table] != right[table]:
            mismatches.append({"table": table, "left_rows": sum(left[table].values()),
                               "right_rows": sum(right[table].values()),
                               "left_only": sum((left[table] - right[table]).values()),
                               "right_only": sum((right[table] - left[table]).values())})
    print(json.dumps({"tables_compared": len(left), "identities_and_content_match": not mismatches,
                      "mismatches": mismatches}, ensure_ascii=False, indent=2))
    raise SystemExit(1 if mismatches else 0)


if __name__ == "__main__":
    main()
