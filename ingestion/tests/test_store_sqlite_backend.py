from __future__ import annotations

from sqlalchemy import select

from bpc_ingestion.models import Base, Assunto, ComunicacaoPje, Movimento, Processo, RegistroDatajud
from bpc_ingestion.postgres_store import PostgresStore


def test_application_store_uses_sqlite_conflict_apis(tmp_path):
    path = tmp_path / "app.sqlite"
    store = PostgresStore(f"sqlite:///{path.as_posix()}")
    Base.metadata.create_all(store.engine)
    try:
        run = store.start_collection("datajud", "TRF1", {"test": True})
        hit = {
            "numero_processo": "0000001-00.2026.4.01.3400",
            "datajud_index": "api_publica_trf1", "datajud_id": "TRF1_G1_test",
            "tribunal": "TRF1", "grau": "G1", "classe": {"codigo": 436, "nome": "JEF"},
            "orgao_julgador": {"codigo": 743, "nome": "Vara Teste"}, "nivel_sigilo": 0,
            "data_ajuizamento": "2026-01-01T00:00:00", "data_ultima_atualizacao": "2026-10-01T00:00:00",
            "cursor_sort": [], "payload_original": {"numeroProcesso": "00000010020264013400"},
            "coletado_em": "2026-10-07T00:00:00+00:00", "assuntos": [{"codigo": 11946, "nome": "Deficiente"}],
            "movimentacoes": [{"codigo": 1, "nome": "Distribuição", "data_hora": "2026-01-01T00:00:00", "complementos": []}],
        }
        assert store.upsert_datajud([hit], run) == 1
        assert store.upsert_datajud([hit], run) == 1
        assert store.save_pje_result("0000001-00.2026.4.01.3400", "encontrado", 1, 200,
            [{"id": "p1", "siglaTribunal": "TRF1", "tipoComunicacao": "Sentença",
              "tipoDocumento": "Sentença", "texto": "Publicado"}], None) == 1
        assert store.save_pje_result("0000001-00.2026.4.01.3400", "encontrado", 1, 200,
            [{"id": "p1", "siglaTribunal": "TRF1", "tipoComunicacao": "Sentença",
              "tipoDocumento": "Sentença", "texto": "Publicado"}], None) == 1
        with store.Session() as session:
            assert session.scalar(select(Processo.id).where(Processo.numero_processo == hit["numero_processo"]))
            assert session.scalar(select(RegistroDatajud.id))
            assert session.scalar(select(Assunto.codigo)) == 11946
            assert session.scalar(select(Movimento.id))
            assert len(session.scalars(select(ComunicacaoPje.id)).all()) == 1
    finally:
        store.close()
