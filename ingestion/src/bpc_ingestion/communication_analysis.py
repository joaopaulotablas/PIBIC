"""Local-only preparation and validation for published communication analysis."""
from __future__ import annotations

import re
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import ComunicacaoPje, ExtracaoIa, Processo

TYPE = "comunicacao_bpc_texto"
PROMPT_VERSION = "ipeaia_comunicacoes_v1"
MAX_COMMUNICATIONS = 20
MAX_TOTAL_CHARS = 60_000
MAX_TEXT_CHARS = 20_000
COMMUNICATION_ANALYSIS_PROMPT = """Versão ipeaia_comunicacoes_v1.
Analise somente as comunicações publicadas fornecidas para um mesmo processo.
Responda em português, com resumo_caso natural e JSON válido. Separe:
motivo_judicializacao (demora_administrativa, implantacao_beneficio,
concessao_inicial, revisao, restabelecimento, outro ou indeterminado),
motivo_administrativo_negativa (somente o motivo expresso da negativa, ou
indeterminado) e resultado_judicial (procedente, improcedente, parcial,
extinto_sem_merito, ordem_processual ou indeterminado). Não trate demora,
implantação, concessão inicial, revisão e restabelecimento como equivalentes.
Não infira negativa administrativa nem mérito a partir de rótulo, alegação ou
andamento. Toda classificação substantiva deve ter evidência com comunicacao_id,
hash_conteudo, trecho_sustentacao copiado exatamente de texto_minimizado e
sustenta igual ao nome do campo. Evidências devem pertencer ao mesmo processo.
Sem trecho suficiente, use indeterminado e descreva a lacuna. Não reproduza,
reconstrua ou infira dados pessoais. status_validacao deve ser pendente.
Formato: {resumo_caso, motivo_judicializacao, motivo_administrativo_negativa,
resultado_judicial, evidencias, lacunas, status_validacao}."""

# Conservative deterministic minimization. Entire identity/contact lines are
# removed; common direct identifiers and title-cased person-name tokens are masked.
_IDENTITY_LINE = re.compile(
    r"(?im)^.*(?:parte\s+(?:autora|r[eé])|polo\s+(?:ativo|passivo)|"
    r"impetrante|requerente|autor(?:a)?|benefici[aá]ri[oa]|advogad[oa]s?|"
    r"representante|endere[cç]o|residente|domiciliad[oa]|telefone|e-?mail)\s*:.*$"
)
_CPF = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
_CNJ = re.compile(r"(?<!\d)\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}(?!\d)")
_EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_URL = re.compile(r"https?://\S+", re.IGNORECASE)
_PHONE = re.compile(r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[- ]?\d{4}(?!\d)")
_LONG_NUMBER = re.compile(r"(?<!\d)\d{5,}(?!\d)")
_DATE = re.compile(r"(?<!\d)(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})(?!\d)")
_TITLE_WORD = re.compile(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]{2,}\b")
_UPPER_NAME = re.compile(r"\b(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,}\s+){1,4}[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,}\b")
_INITIALS = re.compile(r"\b(?:[A-ZÁÉÍÓÚÂÊÔÃÕÇ]\.\s*){2,6}")
_UPPER_PERSON = re.compile(
    r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,}(?:\s+(?:DA|DE|DO|DAS|DOS|E)\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{2,})+\b"
)
_ALL_CAPS = re.compile(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{3,}\b")
_STREET_ADDRESS = re.compile(
    r"\b(?:RUA|AV\.?|AVENIDA|QUADRA|QD\.?|LOTE|LT\.?|ALAMEDA|TRAVESSA)\b[^,;]{0,100}",
    re.IGNORECASE,
)


def minimize_text(text: str) -> str:
    """Remove direct identifiers while retaining a conservative text excerpt."""
    # Court cover pages commonly include full names and physical addresses.
    heading = re.search(r"\b(?:SENTEN[ÇC]A|DECIS[ÃA]O|AC[ÓO]RD[ÃA]O)\b", text, re.IGNORECASE)
    if heading and heading.start() > 0:
        text = text[heading.start():]
    if "\n" in text:
        text = _IDENTITY_LINE.sub("[DADO PESSOAL REMOVIDO]", text)
    markers: dict[str, str] = {}
    # Protect operative legal language before broad name-pattern matching.
    def protect(match: re.Match[str]) -> str:
        token = "\ue000" + chr(0xe100 + len(markers)) + "\ue001"
        markers[token] = match.group(0)
        return token
    text = re.sub(
        r"\b(?:JULGO\s+(?:IMPROCEDENTE|PROCEDENTE|PARCIALMENTE\s+PROCEDENTE)|"
        r"EXTINGO|CONCEDO|INDEFIRO|DEFIRO|DETERMINO|SENTENÇA|DECISÃO|ACÓRDÃO)\b",
        protect, text, flags=re.IGNORECASE,
    )
    for pattern in (_STREET_ADDRESS, _CPF, _CNJ, _EMAIL, _URL, _PHONE, _DATE,
                    _LONG_NUMBER, _INITIALS, _UPPER_PERSON, _UPPER_NAME):
        text = pattern.sub("[DADO PESSOAL REMOVIDO]", text)
    legal_caps = {
        "BPC", "LOAS", "CPC", "CF", "TRF1", "PJE", "INSS", "MPF", "STF",
        "STJ", "CJF", "CNJ", "CRPS", "DER", "AJG", "RPV", "COREJ", "PRESI",
        "MS", "DF", "GO", "MG", "CPF", "SSJ", "JR", "SENTENÇA", "DECISÃO",
        "ACÓRDÃO", "RELATÓRIO", "DISPOSITIVO", "FUNDAMENTAÇÃO", "MANDADO",
        "SEGURANÇA", "PROCESSO", "CLASSE", "IMPETRANTE", "IMPETRADO", "AUTOR",
        "AUTORA", "RÉU", "RÉ", "REQUERENTE", "REQUERIDO", "LITISCONSORTE",
        "REPRESENTANTE", "JUIZ", "FEDERAL", "JUSTIÇA", "VARA", "DEFIRO",
        "INDEFIRO", "JULGO", "EXTINGO", "CONCEDO", "DETERMINO", "INTIME-SE",
    }
    text = _ALL_CAPS.sub(lambda m: m.group(0) if m.group(0) in legal_caps else "[PESSOA]", text)
    # Names are usually title-cased; preserve a small legal vocabulary.
    legal_terms = {
        "Benefício", "Assistencial", "Prestação", "Continuada", "Federal",
        "Justiça", "Juizado", "Especial", "Sentença", "Decisão", "Processo",
        "Tribunal", "União", "Instituto", "Nacional", "Seguro", "Social",
        "Recurso", "Mandado", "Segurança", "Administrativo", "Judicial",
        "Brasília", "Goiás", "Distrito", "Federal", "Código", "Civil",
        "Constituição", "República", "Lei", "Artigo", "Relatório", "Voto",
        "Ante", "Diante", "Assim", "Publique-se", "Intimem-se", "Defiro",
        "Indefiro", "Julgo", "Extingo", "Concedo", "Determino", "INSS",
        "BPC", "LOAS", "CPC", "CF", "TRF1", "PJe",
    }
    def scrub(match: re.Match[str]) -> str:
        word = match.group(0)
        return word if word in legal_terms else "[PESSOA]"
    text = _TITLE_WORD.sub(scrub, text)
    for token, original in markers.items():
        text = text.replace(token, original)
    return re.sub(r"[ \t]+", " ", text).strip()


def prepare_inputs(session: Session, limit: int = MAX_COMMUNICATIONS) -> list[dict[str, Any]]:
    if not 1 <= limit <= MAX_COMMUNICATIONS:
        raise ValueError(f"--limit deve estar entre 1 e {MAX_COMMUNICATIONS}")
    rows = session.execute(
        select(Processo.id, ComunicacaoPje.id, ComunicacaoPje.hash_conteudo,
               ComunicacaoPje.tipo_documento, ComunicacaoPje.tipo_comunicacao,
               ComunicacaoPje.data_disponibilizacao, ComunicacaoPje.texto)
        .join(ComunicacaoPje, ComunicacaoPje.processo_id == Processo.id)
        .where(ComunicacaoPje.texto.is_not(None), ComunicacaoPje.texto != "")
        .order_by(ComunicacaoPje.id)
    ).all()
    if len(rows) > limit:
        rows = rows[:limit]
    packed: list[dict[str, Any]] = []
    total = 0
    by_process: dict[int, dict[str, Any]] = {}
    for process_id, comm_id, digest, doc_type, comm_type, published, text in rows:
        clean = minimize_text(text)
        if len(clean) > MAX_TEXT_CHARS:
            raise ValueError(f"Comunicação {comm_id} excede {MAX_TEXT_CHARS} caracteres após minimização")
        total += len(clean)
        by_process.setdefault(process_id, {"processo_id": process_id, "comunicacoes": []})
        by_process[process_id]["comunicacoes"].append({
            "comunicacao_id": comm_id,
            "hash_conteudo": digest,
            "tipo_publicado": doc_type or comm_type,
            "data_publicacao": published.isoformat() if published else None,
            "texto_minimizado": clean,
        })
    if total > MAX_TOTAL_CHARS:
        raise ValueError(f"Entrada excede {MAX_TOTAL_CHARS} caracteres no total")
    packed.extend(by_process.values())
    return packed


def validate_result(result: dict[str, Any], source: Iterable[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ValueError("resultado deve ser um objeto JSON")
    comms = [comm for process in source for comm in process.get("comunicacoes", [])]
    sources = {int(x["comunicacao_id"]): x for x in comms}
    evidence = result.get("evidencias")
    if not isinstance(evidence, list):
        raise ValueError("evidencias deve ser uma lista")
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("evidência inválida")
        cid = item.get("comunicacao_id")
        source_item = sources.get(cid) if type(cid) is int else None
        if not source_item or item.get("hash_conteudo") != source_item["hash_conteudo"]:
            raise ValueError("evidência sem vínculo de comunicação/hash válido")
        passage = item.get("trecho_sustentacao")
        if not isinstance(passage, str) or not passage.strip() or passage not in source_item["texto_minimizado"]:
            raise ValueError("trecho de evidência ausente na entrada minimizada")
        if not isinstance(item.get("sustenta"), str) or not item["sustenta"].strip():
            raise ValueError("evidência deve indicar o que sustenta")
        if item["sustenta"] not in {
            "motivo_judicializacao", "motivo_administrativo_negativa", "resultado_judicial"
        }:
            raise ValueError("evidência referencia campo analítico desconhecido")
    fields = ("motivo_judicializacao", "motivo_administrativo_negativa", "resultado_judicial")
    for field in fields:
        if field not in result:
            raise ValueError(f"campo obrigatório ausente: {field}")
        value = result[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} deve ser texto ou indeterminado")
        if value != "indeterminado" and not any(e.get("sustenta") == field for e in evidence):
            raise ValueError(f"{field} sem evidência; use indeterminado quando não sustentado")
    if result["motivo_judicializacao"] not in {
        "demora_administrativa", "implantacao_beneficio", "concessao_inicial",
        "revisao", "restabelecimento", "outro", "indeterminado",
    }:
        raise ValueError("motivo_judicializacao fora do vocabulário contratado")
    if result["resultado_judicial"] not in {
        "procedente", "improcedente", "parcial", "extinto_sem_merito",
        "ordem_processual", "indeterminado",
    }:
        raise ValueError("resultado_judicial fora do vocabulário contratado")
    if (not isinstance(result.get("resumo_caso"), str)
            or not result["resumo_caso"].strip() or len(result["resumo_caso"]) > 1500):
        raise ValueError("resumo_caso deve ser texto não vazio com até 1500 caracteres")
    if (not isinstance(result.get("lacunas"), list)
            or any(not isinstance(x, str) or not x.strip() for x in result["lacunas"])):
        raise ValueError("lacunas deve ser uma lista de textos não vazios")
    result["tipo_extracao"] = TYPE
    result["versao_prompt"] = PROMPT_VERSION
    result["status_validacao"] = "pendente"
    return result


def validate_prepared_source(session: Session, process_source: dict[str, Any]) -> None:
    """Ensure an imported preview still matches the published DB text/hash."""
    process_id = process_source.get("processo_id")
    communications = process_source.get("comunicacoes")
    if type(process_id) is not int or not isinstance(communications, list) or not communications:
        raise ValueError("entrada preparada sem processo/comunicacoes validos")
    seen: set[int] = set()
    for item in communications:
        comm_id = item.get("comunicacao_id") if isinstance(item, dict) else None
        if type(comm_id) is not int or comm_id in seen:
            raise ValueError("comunicacao ausente ou duplicada na entrada preparada")
        seen.add(comm_id)
        current = session.scalar(select(ComunicacaoPje).where(
            ComunicacaoPje.id == comm_id,
            ComunicacaoPje.processo_id == process_id,
            ComunicacaoPje.hash_conteudo == item.get("hash_conteudo"),
        ))
        if current is None or minimize_text(current.texto or "") != item.get("texto_minimizado"):
            raise ValueError("entrada preparada nao corresponde ao texto publicado com o ID/hash informado")


def store_result(
    session: Session, process_id: int, result: dict[str, Any], model: str = "local-import"
) -> ExtracaoIa:
    """Insert a new extraction only; never update or replace previous results."""
    extraction = ExtracaoIa(
        processo_id=process_id, tipo_extracao=TYPE, modelo=model,
        versao_prompt=PROMPT_VERSION, resultado=result, status_validacao="pendente",
    )
    session.add(extraction)
    session.flush()
    return extraction
