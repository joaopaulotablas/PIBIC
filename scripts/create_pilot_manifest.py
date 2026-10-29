"""Create a deterministic stratified CNJ pilot manifest from the consolidated DB."""
from __future__ import annotations

import argparse
import csv
import random
import sqlite3
from collections import defaultdict
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--database", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--seed", type=int, default=20261007)
    p.add_argument("--per-group", type=int, default=25)
    args = p.parse_args()
    c = sqlite3.connect(f"file:{args.database.resolve()}?mode=ro", uri=True)
    rows = c.execute("""
        SELECT p.numero_processo,r.tribunal,r.grau,r.orgao_codigo,r.orgao_nome,
               json_extract(r.payload,'$.orgaoJulgador.codigoMunicipioIBGE'),
               r.data_ajuizamento,a.codigo,a.nome
        FROM processos p JOIN registros_datajud r ON r.processo_id=p.id
        JOIN registro_assuntos ra ON ra.registro_id=r.id JOIN assuntos a ON a.codigo=ra.assunto_codigo
        WHERE r.tribunal='TRF1' AND r.grau IN ('G1','JE')
          AND (r.nivel_sigilo=0 OR r.nivel_sigilo IS NULL)
          AND a.codigo IN (6114,11946,11947)
          AND CAST(json_extract(r.payload,'$.orgaoJulgador.codigoMunicipioIBGE') AS INTEGER) IN (743,1798,2788)
        ORDER BY p.numero_processo,r.data_ajuizamento,r.id,a.codigo
    """).fetchall()
    by_process = {}
    for cnj, tribunal, grade, org_code, organ, municipio_code, date_filed, subject_code, subject_name in rows:
        group = {743: "nucleo_trf1_df", 1798: "candidato_ride_formosa", 2788: "candidato_ride_luziania"}[municipio_code]
        key = (cnj, group)
        item = by_process.setdefault(key, {"cnj": cnj, "tribunal": tribunal, "grau": grade,
            "orgao_codigo": org_code, "municipio_codigo": municipio_code,
            "orgao": organ, "data_ajuizamento": date_filed,
            "assuntos": {}, "grupo": group})
        item["assuntos"][subject_code] = subject_name
    candidates = defaultdict(list)
    for item in by_process.values():
        year = (item["data_ajuizamento"] or "")[:4]
        codes = sorted(item["assuntos"])
        family = next((code for code in (11946, 11947, 6114) if code in item["assuntos"]), codes[0])
        item["ano"] = year or "sem_data"
        item["estrato_assunto"] = str(family)
        item["motivo_inclusao"] = ("TRF1, órgão do DF (código local 743), grau G1/JE, assunto 6114 ou descendente TPU; "
                                    "residência não verificada" if item["grupo"] == "nucleo_trf1_df" else
                                    "TRF1, subseção de Formosa/Luziânia na RIDE, grau G1/JE, assunto 6114 ou descendente TPU; "
                                    "residência não verificada")
        candidates[item["grupo"]].append(item)
    rng = random.Random(args.seed)
    selected = []
    for group, quota in (("nucleo_trf1_df", args.per_group), ("candidato_ride_formosa", args.per_group // 2),
                         ("candidato_ride_luziania", args.per_group - args.per_group // 2)):
        strata = defaultdict(list)
        for item in candidates[group]:
            strata[(item["ano"], item["estrato_assunto"])].append(item)
        for pool in strata.values():
            rng.shuffle(pool)
        keys = sorted(strata)
        picked = []
        while keys and len(picked) < quota:
            next_keys = []
            for key in keys:
                if strata[key] and len(picked) < quota:
                    picked.append(strata[key].pop())
                if strata[key]:
                    next_keys.append(key)
            keys = next_keys
        selected.extend(picked)
    selected_cnj = {x["cnj"] for x in selected}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as f:
        fields = ["cnj", "tribunal", "grau", "orgao", "orgao_codigo", "assuntos_codigo_nome",
                  "municipio_codigo_datajud", "ano", "grupo", "motivo_inclusao", "semente", "metodo"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for item in sorted(selected, key=lambda x: (x["grupo"], x["ano"], x["cnj"])):
            w.writerow({"cnj": item["cnj"], "tribunal": item["tribunal"], "grau": item["grau"],
                "orgao": item["orgao"], "orgao_codigo": item["orgao_codigo"],
                "municipio_codigo_datajud": item["municipio_codigo"],
                "assuntos_codigo_nome": "; ".join(f"{k}:{item['assuntos'][k]}" for k in sorted(item["assuntos"])),
                "ano": item["ano"], "grupo": item["grupo"], "motivo_inclusao": item["motivo_inclusao"],
                "semente": args.seed, "metodo": "round-robin estratificado por ano e assunto; shuffle local"})
    print(f"piloto={len(selected)} candidatos={len(by_process)} selecionados_unicos={len(selected_cnj)}")
    for group in sorted(candidates):
        print(f"{group}: pool={len(candidates[group])} selecionados={sum(x['grupo']==group for x in selected)}")


if __name__ == "__main__":
    main()
