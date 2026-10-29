"""Importa somente contagens municipais do Censo SUAS, sem linhas individuais."""
from __future__ import annotations

import csv
import hashlib
import io
import re
import zipfile
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from .inss_benefits import UF_NAMES, fold
from .models import IndicadorSuasMunicipio


ANO = 2025
ARQUIVOS = {
    "cras": "https://aplicacoes.mds.gov.br/snas/defeso/censosuas/2025/1_CRAS.zip",
    "posto_cadastramento": "https://aplicacoes.mds.gov.br/snas/defeso/censosuas/2025/8_POSTO_DE_CADASTRAMENTO.zip",
}
MAX_ZIP_BYTES = 128 * 1024 * 1024
MAX_CSV_BYTES = 160 * 1024 * 1024
MAX_EXPANDED_BYTES = 1024 * 1024 * 1024


def _uf_code(value: Any) -> str:
    key = fold(value).strip()
    if len(key) == 2 and key.upper() in UF_NAMES:
        return key.upper()
    names = {fold(name): code for code, name in UF_NAMES.items()}
    if key in names:
        return names[key]
    raise ValueError(f"UF ausente ou desconhecida no Censo SUAS: {value!r}")


def aggregate_zip(body: bytes, tipo_unidade: str) -> tuple[list[dict[str, Any]], dict[str, int], str]:
    """Agrega identificadores únicos de unidades por município; lê apenas Dados Gerais."""
    if tipo_unidade not in ARQUIVOS:
        raise ValueError(f"Tipo de unidade não suportado: {tipo_unidade}")
    if not body.startswith(b"PK") or len(body) > MAX_ZIP_BYTES:
        raise ValueError("Resposta não é um ZIP válido ou excede 128 MiB")
    digest = hashlib.sha256(body).hexdigest()
    try:
        archive = zipfile.ZipFile(io.BytesIO(body))
    except zipfile.BadZipFile as exc:
        raise ValueError("ZIP Censo SUAS inválido") from exc
    with archive:
        infos = archive.infolist()
        if sum(item.file_size for item in infos) > MAX_EXPANDED_BYTES:
            raise ValueError("ZIP Censo SUAS excede 1 GiB expandido")
        members = [item for item in infos if item.filename.lower().endswith(".csv")
                   and "dados_gerais" in fold(item.filename).replace(" ", "_")
                   and "_rh" not in fold(item.filename).replace(" ", "_")]
        if len(members) != 1:
            raise ValueError(f"Esperado um CSV Dados Gerais; encontrados {len(members)}")
        member = members[0]
        if member.file_size > MAX_CSV_BYTES:
            raise ValueError("CSV Dados Gerais excede 160 MiB")
        city_rows: dict[str, dict[str, Any]] = {}
        seen: dict[str, str] = {}
        row_count = duplicate_count = 0
        with archive.open(member, "r") as raw:
            text = io.TextIOWrapper(raw, encoding="cp1252", newline="")
            reader = csv.DictReader(text, delimiter=";")
            fields = {fold(name).replace(" ", ""): name for name in (reader.fieldnames or [])}
            required = {"codigo": "ibge7", "municipio": "municipio", "uf": "uf",
                        "identificador": "nu_identificador"}
            missing = [label for label, key in required.items() if key not in fields]
            if missing:
                raise ValueError(f"CSV Dados Gerais sem campos obrigatórios: {missing}")
            for row in reader:
                if not row or not any((value or "").strip() for value in row.values() if isinstance(value, str)):
                    continue
                row_count += 1
                code = re.sub(r"\D", "", str(row.get(fields[required["codigo"]]) or ""))
                if not re.fullmatch(r"\d{7}", code):
                    raise ValueError(f"Código IBGE7 inválido na linha de dados {row_count + 1}")
                name = str(row.get(fields[required["municipio"]]) or "").strip()
                identifier = str(row.get(fields[required["identificador"]]) or "").strip()
                if not name or not identifier:
                    raise ValueError(f"Município ou identificador vazio na linha {row_count + 1}")
                uf = _uf_code(row.get(fields[required["uf"]]))
                prior_city = seen.get(identifier)
                if prior_city is not None:
                    if prior_city != code:
                        raise ValueError("Identificador de unidade repetido em municípios diferentes")
                    duplicate_count += 1
                    continue
                seen[identifier] = code
                existing = city_rows.get(code)
                if existing is not None and (existing["municipio_nome"] != name or existing["uf"] != uf):
                    raise ValueError(f"Rótulo municipal divergente para o código IBGE {code}")
                if existing is None:
                    city_rows[code] = {"codigo_ibge": code, "municipio_nome": name, "uf": uf,
                                       "ids": set()}
                city_rows[code]["ids"].add(identifier)
        if row_count == 0:
            raise ValueError("CSV Dados Gerais sem registros")
    records = [{"tipo_unidade": tipo_unidade, "codigo_ibge": code,
                "municipio_nome": item["municipio_nome"], "uf": item["uf"],
                "quantidade_unidades": len(item["ids"])}
               for code, item in sorted(city_rows.items())]
    quality = {"linhas_lidas": row_count, "unidades_unicas": len(seen),
               "linhas_unidade_duplicadas": duplicate_count, "municipios": len(records)}
    return records, quality, digest


def store_aggregates(session, records: list[dict[str, Any]], *, ano: int, url: str,
                     raw_path: str, digest: str, run_id) -> int:
    inserted = 0
    for record in records:
        key = {"ano": ano, "tipo_unidade": record["tipo_unidade"],
               "codigo_ibge": record["codigo_ibge"], "hash_arquivo": digest}
        existing = session.scalar(select(IndicadorSuasMunicipio).filter_by(**key))
        if existing is not None:
            if (existing.quantidade_unidades != record["quantidade_unidades"]
                    or existing.municipio_nome != record["municipio_nome"]
                    or existing.uf != record["uf"]):
                raise ValueError("ZIP idêntico produziu agregação divergente")
            continue
        session.add(IndicadorSuasMunicipio(
            fonte="mds_censo_suas", ano=ano, tipo_unidade=record["tipo_unidade"],
            codigo_ibge=record["codigo_ibge"], municipio_nome=record["municipio_nome"],
            uf=record["uf"], quantidade_unidades=record["quantidade_unidades"],
            url_origem=url, arquivo_bruto=raw_path, hash_arquivo=digest,
            coleta_id=run_id, coletado_em=datetime.now(timezone.utc),
        ))
        inserted += 1
    return inserted
