"""Case review persistence and source identity, using synthetic records only."""
import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from bpc_ingestion import api
from bpc_ingestion.database import make_engine
from bpc_ingestion.models import Base, Processo, DocumentoPublico, DocumentoProcesso, Coleta
from bpc_ingestion.research import RevisaoCaso


@pytest.fixture
def case(tmp_path, monkeypatch):
    engine = make_engine(f"sqlite:///{tmp_path / 'review.sqlite'}")
    Base.metadata.create_all(engine)
    monkeypatch.setattr(api, "engine", engine)
    monkeypatch.setattr(api, "SessionLocal", sessionmaker(engine))
    with Session(engine) as session:
        p = Processo(numero_processo="0000001-00.2026.4.01.0000")
        other = Processo(numero_processo="0000002-00.2026.4.01.0000")
        run = Coleta(id=uuid.uuid4(), fonte="sintetico", status="concluida", parametros={})
        session.add_all([p, other, run]); session.flush()
        d = DocumentoPublico(fonte="pje_trf1", documento_id="1", hash_conteudo="a"*64,
            tipo_documento="Sentença", numero_origem=p.numero_processo, numeros_cnj=[p.numero_processo],
            texto="DOCUMENTO SINTÉTICO. Pedido de concessão de BPC.", payload={},
            url_origem="https://example.org", recurso_url="https://example.org/documento", arquivo_bruto="synthetic.html.gz",
            coleta_id=run.id, coletado_em=datetime.now(timezone.utc))
        session.add(d); session.flush()
        session.add(DocumentoProcesso(documento_id=d.id, processo_id=p.id, criterio="cnj_explicito"))
        session.commit()
        def override():
            with Session(engine) as request_session:
                yield request_session
        api.app.dependency_overrides[api.get_session] = override
        with TestClient(api.app, base_url="http://localhost", client=("127.0.0.1", 1234)) as client:
            yield client, p, other, d
    api.app.dependency_overrides.clear()
    engine.dispose()


def payload(doc):
    return dict(autor="Pesquisador teste", estado="revisado", inclusao="incluir",
        resumo="Síntese sintética", motivo="Não identificado", observacoes="Documento conferido.",
        evidencias=[dict(documento_id=doc.id,hash_conteudo=doc.hash_conteudo,trecho="Pedido de concessão de BPC.")])


def test_read_save_history_and_conflict(case):
    client, p, _, doc = case
    url=f"/admin/api/pesquisa/{p.numero_processo}"
    read=client.get(url+"/leitura")
    assert read.status_code==200
    assert read.json()["documentos_publicos"][0]["texto"]==doc.texto
    data=payload(doc)
    saved=client.post(url+"/revisoes",json=data,headers={"X-BPC-Review":"1"})
    assert saved.status_code==201
    assert client.post(url+"/revisoes",json=data,headers={"X-BPC-Review":"1"}).status_code==409
    data.update(anterior_id=saved.json()["id"],resumo="Síntese corrigida")
    assert client.post(url+"/revisoes",json=data,headers={"X-BPC-Review":"1"}).status_code==201
    history=client.get(url+"/leitura").json()["revisoes"]
    assert len(history)==2 and history[1]["resumo"]=="Síntese sintética"
    queue=client.get("/admin/api/pesquisa/fila?recorte=false&estado=revisado").json()
    assert queue["total"]==1 and queue["items"][0]["documentos"]==1


def test_quote_and_cross_case_rejected(case):
    client,p,other,doc=case
    data=payload(doc)
    url=f"/admin/api/pesquisa/{p.numero_processo}/revisoes"
    headers={"X-BPC-Review":"1"}
    assert client.post(f"/admin/api/pesquisa/{other.numero_processo}/revisoes",json=data,headers=headers).status_code==422
    data["evidencias"][0]["trecho"]="Trecho inventado"
    assert client.post(url,json=data,headers=headers).status_code==422
    data=payload(doc);data["evidencias"][0]["hash_conteudo"]="incorrect"
    assert client.post(url,json=data,headers=headers).status_code==422


def test_local_access_and_completion(case):
    client,p,_,doc=case
    url=f"/admin/api/pesquisa/{p.numero_processo}"
    assert client.get(url+"/leitura",headers={"Host":"remote.example"}).status_code==403
    assert client.get(url+"/leitura",headers={"Origin":"https://external.example"}).status_code==403
    assert client.post(url+"/revisoes",json=payload(doc)).status_code==403
    data=payload(doc);data["resumo"]=""
    assert client.post(url+"/revisoes",json=data,headers={"X-BPC-Review":"1"}).status_code==422
    assert client.get("/").status_code==200
    assert client.get("/admin/analise.js").status_code==200
