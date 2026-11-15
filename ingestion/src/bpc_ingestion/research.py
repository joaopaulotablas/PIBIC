"""Local case reading and append-only human review."""
from datetime import datetime, timezone
from ipaddress import ip_address
from typing import Literal
from urllib.parse import urlsplit

from fastapi import HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictInt
from sqlalchemy import select
from .models import RevisaoCaso


class ReviewEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    documento_id: StrictInt = Field(ge=1)
    hash_conteudo: str = Field(min_length=64, max_length=64)
    trecho: str = Field(min_length=1, max_length=5000)


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    anterior_id: int | None = Field(default=None, ge=1)
    autor: str = Field(min_length=1, max_length=120)
    estado: Literal["em_revisao", "revisado"] = "em_revisao"
    inclusao: Literal["pendente", "incluir", "excluir"] = "pendente"
    resumo: str = Field(default="", max_length=6000)
    motivo: str = Field(default="", max_length=3000)
    observacoes: str = Field(default="", max_length=6000)
    evidencias: list[ReviewEvidence] = Field(default_factory=list, max_length=50)


def require_local(request: Request):
    def local(host):
        if host == "localhost":
            return True
        try:
            return ip_address(host).is_loopback
        except (ValueError, TypeError):
            return False
    origin = request.headers.get("origin")
    if (not request.client or not local(request.client.host)
            or not local(request.url.hostname)
            or (origin and not local(urlsplit(origin).hostname))):
        raise HTTPException(403, "Leitura e revisão disponíveis pelo endereço local da aplicação.")
    if request.method != "GET" and request.headers.get("x-bpc-review") != "1":
        raise HTTPException(403, "Cabeçalho de revisão local ausente")


def review_json(row):
    if row is None:
        return None
    return {key: getattr(row, key) for key in (
        "id", "autor", "estado", "inclusao", "resumo", "motivo", "observacoes", "evidencias", "criado_em")}


def save_review(session, process_id, payload, documents):
    # Serialize concurrent updates for this case, including its first review.
    from .models import Processo
    if session.get_bind().dialect.name == "postgresql":
        session.execute(select(Processo).where(Processo.id == process_id).with_for_update())
    latest = session.scalar(select(RevisaoCaso).where(RevisaoCaso.processo_id == process_id)
                            .order_by(RevisaoCaso.id.desc()).limit(1))
    if payload.anterior_id != (latest.id if latest else None):
        raise HTTPException(409, "Outra revisão foi salva. Reabra o caso antes de continuar.")
    by_id = {d.id: d for d in documents}
    validated = []
    for evidence in payload.evidencias:
        evidence = evidence.model_dump()
        doc = by_id.get(evidence.get("documento_id"))
        quote = evidence.get("trecho")
        if (doc is None or evidence.get("hash_conteudo") != doc.hash_conteudo
                or not isinstance(quote, str) or not quote.strip() or len(quote) > 5000
                or quote not in (doc.texto or "")):
            raise HTTPException(422, "Evidência deve citar literalmente um documento vinculado e seu hash.")
        validated.append(dict(documento_id=doc.id, hash_conteudo=doc.hash_conteudo, trecho=quote))
    if payload.estado == "revisado" and (not payload.resumo or not payload.observacoes):
        raise HTTPException(422, "Para concluir, preencha síntese e justificativa da revisão.")
    row = RevisaoCaso(processo_id=process_id, autor=payload.autor, estado=payload.estado,
                      inclusao=payload.inclusao, resumo=payload.resumo, motivo=payload.motivo,
                      observacoes=payload.observacoes, evidencias=validated,
                      criado_em=datetime.now(timezone.utc))
    session.add(row)
    session.commit()
    return review_json(row)
