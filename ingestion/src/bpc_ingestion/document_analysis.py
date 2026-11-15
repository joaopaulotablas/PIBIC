"""Local documentary inputs, exact evidence validation and append-only storage.

No network calls here. Preparing data is not privacy approval or human review.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .document_schemas import (
    MAX_CHARS, MAX_DOCUMENTS, MAX_PILOT, PIPELINE_VERSION, PROMPT_VERSION,
    SCHEMA_VERSION, TYPE, DocumentResult,
)
from .models import DocumentoProcesso, DocumentoPublico, ExtracaoIa, Processo
from .pje_public import CNJ, parse_document, soup_html

ABSTENTION_SUMMARY = (
    "Os documentos disponíveis não sustentam uma conclusão sobre a causa da ação "
    "ou seu resultado. A análise depende de revisão humana e de documentação suficiente."
)
_CITATION = re.compile(
    r"\b(?:precedentes?|jurisprud[eê]ncia|ementa|nesse sentido|neste sentido|"
    r"a prop[oó]sito|confira-se|veja-se|colaciono|transcrevo|cita[cç][aã]o|"
    r"s[uú]mula|recurso (?:especial|extraordin[aá]rio)|agravo|relator|rel\.)\b", re.I,
)
# End a conservative precedent region only at an unambiguous operative heading.
_OPERATIVE = re.compile(
    r"(?im)^\s*(?:ante o exposto|diante do exposto|pelo exposto|isto posto|"
    r"isso posto|[IVX.\d\s-]*dispositivo\b)",
)


def text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def payload_digest(payload: dict) -> str:
    return text_digest(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def _all_occurrences(text: str, passage: str) -> list[tuple[int, int]]:
    found, start = [], 0
    while passage and (start := text.find(passage, start)) >= 0:
        found.append((start, start + len(passage)))
        start += 1
    return found


def _raw_body(item: DocumentoPublico, raw_root: Path, local_path: str | None = None) -> tuple[bytes, Path]:
    path = Path(local_path or item.arquivo_bruto).resolve()
    if not path.is_relative_to(raw_root.resolve()) or not path.is_file():
        raise ValueError("bronze_ausente_ou_fora_da_raiz_local")
    if path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("bronze_excede_limite")
    with (gzip.open(path, "rb") if path.suffix == ".gz" else path.open("rb")) as stream:
        body = stream.read(16 * 1024 * 1024 + 1)
    if len(body) > 16 * 1024 * 1024:
        raise ValueError("bronze_expandida_excede_limite")
    return body, path


def excluded_intervals(body: bytes, text: str, number: str) -> list[dict[str, Any]]:
    """Structural quotes plus conservative citation regions; not semantic review."""
    root = soup_html(body).select_one(".folha")
    if root is None:
        raise ValueError("bronze_sem_folha")
    for node in root.select("script, style, noscript, form, #panelGroupPai"):
        node.decompose()
    if root.get_text("\n", strip=True) != text:
        raise ValueError("bronze_texto_divergente")
    ranges: list[tuple[int, int, str]] = []
    for quote in root.select("blockquote, q"):
        passage = quote.get_text("\n", strip=True)
        for start, end in _all_occurrences(text, passage):
            ranges.append((start, end, "citacao_html"))
    # Quoted spans often lose quotation semantics during HTML-to-text conversion.
    for match in re.finditer(r'“[^”]+”|«[^»]+»|"[^"\n]{20,}"', text, re.S):
        ranges.append((match.start(), match.end(), "citacao_delimitada"))
    offset = 0
    for line in text.splitlines(keepends=True):
        foreign = any(m.group() != number for m in re.finditer(CNJ, line))
        if foreign or _CITATION.search(line):
            ending = _OPERATIVE.search(text, offset + len(line))
            ranges.append((offset, ending.start() if ending else len(text), "possivel_precedente"))
        offset += len(line)
    return [dict(inicio=start, fim=end, motivo=reason)
            for start, end, reason in sorted(set(ranges)) if end > start]


def _document_source(session: Session, process: Processo, ref: dict, raw_root: Path,
                     bronze_map: dict[int, str]) -> dict:
    if not isinstance(ref, dict) or type(ref.get("id")) is not int:
        raise ValueError("documento_id_invalido")
    item = session.get(DocumentoPublico, ref["id"])
    link = session.get(DocumentoProcesso, (ref["id"], process.id))
    if item is None or link is None or link.criterio != "cnj_explicito":
        raise ValueError("documento_sem_vinculo_explicito_ao_processo")
    payload = item.payload or {}
    if (item.fonte != "pje_trf1" or item.numeros_cnj != [process.numero_processo]
            or item.numero_origem != process.numero_processo
            or payload.get("numero_processo") != process.numero_processo
            or payload.get("versao_parser") != "pje_publico_v1"
            or payload.get("extracao_texto") != "pje_html_publico"):
        raise ValueError("documento_nao_e_pje_proprio_confirmado")
    if (ref.get("hash_conteudo") != item.hash_conteudo
            or ref.get("documento_id") != item.documento_id
            or payload_digest(payload) != item.hash_conteudo):
        raise ValueError("documento_hash_ou_identidade_divergente")
    if not isinstance(item.texto, str) or not item.texto.strip() or payload.get("texto") != item.texto:
        raise ValueError("texto_ausente_ou_divergente_do_payload")
    body, local_path = _raw_body(item, raw_root, bronze_map.get(item.id))
    try:
        parsed = parse_document(body, process.numero_processo, item.documento_id,
                                item.tipo_documento, item.recurso_url)
    except ValueError as exc:
        raise ValueError("bronze_identidade_documental_invalida") from exc
    if payload_digest(parsed["payload"]) != item.hash_conteudo:
        raise ValueError("bronze_hash_divergente")
    return {
        "documento_id": item.id, "documento_origem_id": item.documento_id,
        "fonte": item.fonte, "hash_conteudo": item.hash_conteudo,
        "sha256_texto": text_digest(item.texto), "tipo_documento": item.tipo_documento,
        "arquivo_bruto_original": item.arquivo_bruto, "arquivo_bruto_local": str(local_path),
        "sha256_bronze": hashlib.sha256(body).hexdigest(),
        "campo": "texto", "texto": item.texto, "caracteres": len(item.texto),
        "intervalos_excluidos": excluded_intervals(body, item.texto, process.numero_processo),
    }


def prepare_process(session: Session, entry: dict, raw_root: Path = Path("data"),
                    bronze_map: dict[int, str] | None = None) -> dict:
    """Load ONLY frozen document versions selected explicitly in the pilot."""
    if not isinstance(entry, dict) or type(entry.get("processo_id")) is not int:
        raise ValueError("processo_id_invalido")
    process = session.get(Processo, entry["processo_id"])
    if process is None or entry.get("cnj") != process.numero_processo:
        raise ValueError("processo_manifesto_divergente")
    refs = entry.get("documentos")
    if not isinstance(refs, list) or not 1 <= len(refs) <= MAX_DOCUMENTS:
        raise ValueError("quantidade_documentos_fora_do_limite")
    ids = [r.get("id") for r in refs if isinstance(r, dict)]
    if any(type(i) is not int for i in ids) or len(set(ids)) != len(refs):
        raise ValueError("documento_id_duplicado_ou_invalido")
    documents = [_document_source(session, process, ref, raw_root, bronze_map or {}) for ref in refs]
    total = sum(d["caracteres"] for d in documents)
    if total > MAX_CHARS:
        raise ValueError("texto_excede_limite_sem_truncamento")
    return dict(processo_id=process.id, numero_processo=process.numero_processo,
                documentos=documents, caracteres=total, texto_truncado=False,
                revisao_privacidade="pendente", revisao_humana="pendente")


def prepare_pilot(session: Session, entries: list, raw_root: Path = Path("data"),
                  bronze_map: dict[int, str] | None = None) -> dict:
    if not isinstance(entries, list) or not 1 <= len(entries) <= MAX_PILOT:
        raise ValueError("piloto_exige_1_a_40_processos_explicitos")
    ids = [e.get("processo_id") for e in entries if isinstance(e, dict)]
    if any(type(i) is not int for i in ids) or len(set(ids)) != len(entries):
        raise ValueError("processo_id_duplicado_ou_invalido")
    ready, blocked = [], []
    for entry in entries:
        try:
            ready.append(prepare_process(session, entry, raw_root, bronze_map))
        except (ValueError, OSError, EOFError) as exc:
            # Safe codes only: malformed HTML and paths may contain personal data.
            reason = str(exc) if isinstance(exc, ValueError) else "bronze_ilegivel"
            if not re.fullmatch(r"[a-z_]{1,100}", reason):
                reason = "fonte_nao_validada_verificar_documentos_e_bronze"
            blocked.append(dict(processo_id=entry["processo_id"],
                                motivo=reason))
    return dict(tipo_extracao=TYPE, versao_prompt=PROMPT_VERSION,
                versao_schema=SCHEMA_VERSION, versao_pipeline=PIPELINE_VERSION,
                selecionados=len(entries), processos=ready, bloqueados=blocked,
                chamadas_externas_executadas=0, envio_externo_permitido=False,
                bloqueio_envio="plano_exige_dados_pessoais_exclusivamente_locais",
                revisao_humana="pendente", revisao_privacidade="pendente")


def validate_prepared_source(session: Session, source: dict, raw_root: Path = Path("data")) -> None:
    refs = [dict(id=d["documento_id"], documento_id=d["documento_origem_id"],
                 hash_conteudo=d["hash_conteudo"]) for d in source["documentos"]]
    current = prepare_process(session, dict(processo_id=source["processo_id"],
                              cnj=source["numero_processo"], documentos=refs), raw_root,
                              {d["documento_id"]: d["arquivo_bruto_local"] for d in source["documentos"]})
    if current != source:
        raise ValueError("entrada_preparada_diverge_do_banco_ou_bronze")


def validate_result(result: Any, source: dict) -> dict:
    parsed = DocumentResult.model_validate(result)
    normalized = parsed.model_dump()
    docs = {d["documento_id"]: d for d in source["documentos"]}
    supported = set()
    for evidence in parsed.evidencias:
        doc = docs.get(evidence.documento_id)
        if doc is None or evidence.hash_conteudo != doc["hash_conteudo"]:
            raise ValueError("evidencia_documento_hash_fora_do_processo")
        start, end = evidence.inicio, evidence.fim
        if (not evidence.trecho.strip() or not start < end <= len(doc["texto"])
                or doc["texto"][start:end] != evidence.trecho):
            raise ValueError("evidencia_trecho_ou_localizacao_divergente")
        if any(start < r["fim"] and end > r["inicio"] for r in doc["intervalos_excluidos"]):
            raise ValueError("evidencia_em_citacao_ou_jurisprudencia_alheia")
        if any(m.group() != source["numero_processo"] for m in re.finditer(CNJ, evidence.trecho)):
            raise ValueError("evidencia_em_processo_alheio")
        supported.add(evidence.sustenta)
    for name in ("provavel_causa", "ato_administrativo", "negativa_administrativa",
                 "requisito_controvertido", "fundamento_judicial"):
        value = normalized[name]
        if not value.strip() or (value != "indeterminado" and name not in supported):
            raise ValueError(f"{name}_sem_evidencia_use_indeterminado")
    for name, value in normalized["desfecho"].items():
        if value != "indeterminado" and f"desfecho.{name}" not in supported:
            raise ValueError(f"desfecho.{name}_sem_evidencia_use_indeterminado")
    if parsed.desfecho.natureza == "final":
        final_quotes = [e.trecho for e in parsed.evidencias if e.sustenta == "desfecho.natureza"]
        if all(re.search(r"tutela|provis[oó]ri|liminar|antecipa[cç][aã]o", q, re.I)
               and not re.search(r"julgo|senten[cç]a|ac[oó]rd[aã]o|extingo|resolvo.*m[eé]rito", q, re.I)
               for q in final_quotes):
            raise ValueError("tutela_provisoria_nao_prova_decisao_final")
    if normalized["resumo_caso"] != ABSTENTION_SUMMARY and "resumo_caso" not in supported:
        raise ValueError("resumo_caso_sem_evidencia_use_resumo_de_abstencao")
    if any(not x.strip() for x in parsed.lacunas):
        raise ValueError("lacunas_vazias")
    return normalized


def provenance(source: dict) -> list[dict]:
    keys = ("documento_id", "documento_origem_id", "fonte", "hash_conteudo", "sha256_texto", "sha256_bronze")
    return [{key: doc[key] for key in keys} for doc in source["documentos"]]


def store_result(session: Session, source: dict, result: Any, model: str,
                 raw_root: Path = Path("data"), origin: str = "importacao_local") -> ExtracaoIa:
    """Validate both source and result before storing; never overwrite history."""
    if not isinstance(model, str) or not model.strip() or len(model) > 100:
        raise ValueError("modelo_real_obrigatorio_ate_100_caracteres")
    if origin != "importacao_local":
        raise ValueError("envio_documental_externo_bloqueado_por_privacidade")
    validate_prepared_source(session, source, raw_root)
    result = validate_result(result, source)
    stored = dict(result, versao_schema=SCHEMA_VERSION, versao_pipeline=PIPELINE_VERSION,
                  proveniencia=provenance(source), origem_execucao=origin,
                  revisao_privacidade="pendente", chamadas_externas_executadas=0)
    existing = session.scalar(select(ExtracaoIa).where(
        ExtracaoIa.processo_id == source["processo_id"], ExtracaoIa.tipo_extracao == TYPE,
        ExtracaoIa.modelo == model, ExtracaoIa.versao_prompt == PROMPT_VERSION))
    if existing:
        if existing.resultado == stored:
            return existing
        raise ValueError("extracao_existente_divergente_requer_nova_versao_de_prompt")
    count = session.scalar(select(func.count()).select_from(ExtracaoIa).where(
        ExtracaoIa.tipo_extracao == TYPE)) or 0
    if count >= MAX_PILOT:
        raise ValueError("gate_humano_necessario_apos_40_resultados")
    row = ExtracaoIa(processo_id=source["processo_id"], tipo_extracao=TYPE, modelo=model,
                     versao_prompt=PROMPT_VERSION, resultado=stored, status_validacao="pendente")
    session.add(row)
    session.flush()
    return row


def extraction_json(item: ExtracaoIa, include_local_text: bool = False) -> dict:
    """Explicit local reading only; privacy gate is enforced by the HTTP caller."""
    result = item.resultado if include_local_text else None
    return dict(id=item.id, tipo_extracao=item.tipo_extracao, modelo=item.modelo,
                versao_prompt=item.versao_prompt, resultado=result,
                proveniencia=(item.resultado or {}).get("proveniencia", []),
                status_validacao=item.status_validacao, revisao_humana="pendente",
                revisao_privacidade="pendente", texto_retido=not include_local_text,
                confianca=item.confianca, criado_em=item.criado_em)
