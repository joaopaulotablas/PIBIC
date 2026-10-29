"""Read-only local inventory. Lexical matches are NOT case classifications."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

VERSION = "disponibilidade_textual_v1"
# Deliberately bounded expressions: exported matches contain vocabulary, not
# names, context windows, medical descriptions or other personal case details.
CUES = {
    "bpc_loas": r"\b(?:BPC|LOAS|benef[ií]cio\s+assistencial|presta[çc][ãa]o\s+continuada)\b",
    "renda": r"\b(?:renda\s+(?:familiar|per\s+capita)|miserabilidade|vulnerabilidade\s+social)\b",
    "deficiencia": r"\b(?:defici[êe]ncia|impedimento\s+de\s+longo\s+prazo)\b",
    "idade": r"\b(?:idoso|idosa|65\s+anos)\b",
    "demora": r"\b(?:demora\s+administrativa|mora\s+administrativa|prazo\s+razo[aá]vel)\b",
    "cadastro": r"\b(?:Cad[ÚUuú]nico|cadastro\s+[úu]nico)\b",
    "cessacao": r"\b(?:cessa[çc][ãa]o|restabelecimento)\b",
    "indeferimento_administrativo": r"\b(?:indeferimento\s+administrativo|indeferido\s+administrativamente)\b",
    "dispositivo": r"\b(?:julgo\s+(?:improcedente|procedente|parcialmente\s+procedente)|"
                   r"nego\s+provimento|dou\s+provimento|concedo\s+a\s+seguran[çc]a|extingo\s+o\s+processo)\b",
    "fundamentacao": r"\b(?:fundamenta[çc][ãa]o|relat[óo]rio|voto)\b",
}
PATTERNS = {name: re.compile(expression, re.IGNORECASE) for name, expression in CUES.items()}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def inspect_item(kind: str, row: dict, links: list[int]) -> dict:
    fields = ("texto", "ementa", "decisao") if kind == "documento" else ("texto",)
    available = {field: row.get(field) for field in fields
                 if isinstance(row.get(field), str) and row[field].strip()}
    occurrences = []
    for field, text in available.items():
        for label, pattern in PATTERNS.items():
            # All matches retained for exact locating; no context copied out.
            for match in pattern.finditer(text):
                occurrences.append({"rotulo": label, "campo": field,
                                    "inicio": match.start(), "fim": match.end(),
                                    "expressao": match.group(0)})
    labels = sorted({item["rotulo"] for item in occurrences})
    availability = ("texto_publicado" if "texto" in available else
                    "espelho_ementa" if available else "sem_texto")
    return {
        "tipo": kind, "id": row["id"], "fonte": row["fonte"],
        "identidade_origem": str(row.get("documento_id") or row.get("comunica_id") or row["id"]),
        "hash_conteudo": row["hash_conteudo"], "disponibilidade": availability,
        "campos": {field: {"caracteres": len(text), "sha256_texto": digest(text)}
                   for field, text in available.items()},
        "vinculos_processos": sorted(set(links)), "pistas_lexicais": labels,
        "ocorrencias": occurrences, "revisao_semantica": "pendente",
        "alertas": (["texto_curto"] if available and max(map(len, available.values())) < 600 else [])
                   + (["possivel_markup_residual"] if any(re.search(r"</?(?:html|body|div|p)\b", x,
                                                                 re.IGNORECASE) for x in available.values()) else []),
    }


def audit_database(path: Path) -> dict:
    if not path.is_file():
        raise ValueError("Banco local inexistente")
    connection = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        links = defaultdict(list)
        for row in connection.execute("SELECT documento_id,processo_id FROM documento_processos"):
            links[row[0]].append(row[1])
        records = []
        for row in connection.execute("SELECT id,fonte,documento_id,hash_conteudo,texto,ementa,decisao "
                                      "FROM documentos_publicos ORDER BY id"):
            records.append(inspect_item("documento", dict(row), links[row["id"]]))
        for row in connection.execute("SELECT id,processo_id,comunica_id,hash_conteudo,texto "
                                      "FROM comunicacoes_pje ORDER BY id"):
            records.append(inspect_item("comunicacao", dict(row, fonte="comunica_pje"), [row["processo_id"]]))
        groups = defaultdict(list)
        for item in records:
            # One main field per item: do not double count an embedded ementa.
            for field in ("texto", "ementa", "decisao"):
                if field in item["campos"]:
                    groups[item["campos"][field]["sha256_texto"]].append(
                        {"tipo": item["tipo"], "id": item["id"], "campo": field})
                    break
        by_source = {}
        for source in sorted({item["fonte"] for item in records}):
            selected = [item for item in records if item["fonte"] == source]
            by_source[source] = {
                "itens": len(selected),
                "identidades_origem": len({item["identidade_origem"] for item in selected}),
                "disponibilidade": dict(Counter(item["disponibilidade"] for item in selected)),
                "itens_com_pista": {label: sum(label in item["pistas_lexicais"] for item in selected)
                                   for label in PATTERNS},
                "itens_com_vinculo": sum(bool(item["vinculos_processos"]) for item in selected),
            }
        return {
            "versao": VERSION, "gerado_em": datetime.now(timezone.utc).isoformat(),
            "banco": path.name, "metodo": "inventario_lexical_local_sem_IA",
            "aviso": "Pistas lexicais não confirmam motivo, desfecho, inteiro teor, relevância ou anonimização.",
            "por_fonte": by_source, "total_itens": len(records),
            "textos_principais_distintos": len(groups),
            "duplicatas_textuais": [{"sha256_texto": key, "itens": items}
                                    for key, items in sorted(groups.items()) if len(items) > 1],
            "itens": records,
        }
    finally:
        connection.close()


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise ValueError("Saída já existe; use novo nome, sem sobrescrever auditoria")
    result = audit_database(args.database)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
    print(json.dumps({"arquivo": str(args.output), "total_itens": result["total_itens"],
                      "textos_distintos": result["textos_principais_distintos"],
                      "por_fonte": result["por_fonte"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
