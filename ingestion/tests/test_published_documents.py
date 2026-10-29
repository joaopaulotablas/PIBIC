import gzip
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.request import Request

from sqlalchemy import select

from bpc_ingestion.cli import collect_published_documents
from bpc_ingestion.config import Settings
from bpc_ingestion.models import Base, Coleta, DocumentoProcesso, DocumentoPublico, Processo
from bpc_ingestion.postgres_store import PostgresStore
from bpc_ingestion.public_sources import OfficialRedirectHandler, SourceBlocked
from bpc_ingestion.published_documents import official_url, published_documents


TNU = "https://eproctnu-jur.cjf.jus.br/eproc/externo_controlador.php?acao=jurisprudencia%40jurisprudencia%2Fdownload_inteiro_teor&id_jurisprudencia=123"
TRF3 = "https://web.trf3.jus.br/acordaos/Acordao/BuscarDocumentoPje/123"
TRF2 = "https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=jurisprudencia%40jurisprudencia%2Fdownload_inteiro_teor&id_jurisprudencia=123"
TRF4 = "https://jurisprudencia.trf4.jus.br/eproc2trf4/externo_controlador.php?acao=jurisprudencia%40jurisprudencia%2Fdownload_inteiro_teor&id_jurisprudencia=123"
TRF5 = "https://jurisprudencia.trf5.jus.br/jurisprudencia/exibir.wsp?tmp.id_documento=123"
TRF6 = "https://eproc-jur.trf6.jus.br/eproc/externo_controlador.php?acao=jurisprudencia%40jurisprudencia%2Fdownload_inteiro_teor&id_jurisprudencia=123"
NUMBER = "5006875-14.2022.4.04.7005"


def tnu_html(text="Benefício assistencial BPC", number=NUMBER):
    return f'''<html><meta charset="utf-8"><article><header id="900_1">
    <p class="identificacao_processo">Pedido de Uniformização Nº {number}/PR</p></header>
    <section><p class="titulo">VOTO</p><p>{text}</p></section>
    <footer>assinatura variável</footer></article></html>'''.encode()


class PublishedDocumentsTest(unittest.TestCase):
    def test_tnu_original_process_label_is_not_primary_or_link(self):
        original = '5000409-73.2023.4.04.7003'
        body = tnu_html(number=NUMBER + '/PR PROCESSO ORIGINÁRIO: Nº ' + original)
        row = published_documents(body, TNU)[0]
        self.assertEqual(row['numeros_cnj'], [NUMBER])
        self.assertEqual(row['payload']['numero_processo'], NUMBER)
        self.assertIn(original, row['texto'])
        with self.assertRaises(ValueError):
            published_documents(tnu_html(number=NUMBER + ' / ' + original), TNU)
        with self.assertRaises(ValueError):
            published_documents(tnu_html(number='PROCESSO ORIGINÁRIO: Nº ' + original), TNU)

    def test_official_routes_and_canonical_ids(self):
        self.assertEqual(official_url(TNU)[0:2], ("tnu", "123"))
        self.assertEqual(official_url(TNU.replace("%40", "@").replace("%2F", "/")), official_url(TNU))
        self.assertEqual(official_url(TRF3)[0:2], ("trf3_jurisprudencia", "123"))
        self.assertEqual(official_url(TRF2)[0:2], ("trf2_jurisprudencia", "123"))
        self.assertEqual(official_url(TRF4)[0:2], ("trf4_jurisprudencia", "123"))
        self.assertEqual(official_url(TRF5)[0:2], ("trf5_jurisprudencia", "123"))
        self.assertEqual(official_url(TRF6)[0:2], ("trf6_jurisprudencia", "123"))
        self.assertEqual(official_url(TRF6 + "&termosPesquisados=Ynpj")[1], "123")
        for url in [TNU + "&token=secret", TNU + "&id_jurisprudencia=2", TNU + "#x",
                    TRF3.replace("https", "http"), TRF3.replace("web.trf3", "evil.trf3"),
                    TRF3.replace("https://", "https://user:password@"), TRF3.replace(".br/", ".br:444/"),
                    TRF5.replace("123", "abc"), TRF6 + "&token=secret", TRF4 + "&token=secret",
                    TRF2 + "&token=secret"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                official_url(url)

    def test_tnu_article_ids_not_search_id_and_no_citation_links(self):
        body = tnu_html("BPC; precedente 1053078-37.2022.4.01.3400; não vincular citação")
        row = published_documents(body, TNU)[0]
        self.assertEqual(row["documento_id"], "900")
        self.assertEqual(row["numeros_cnj"], [NUMBER])
        self.assertNotIn("assinatura", row["texto"])
        self.assertEqual(row["payload"]["extracao_texto"], "html_publicado")
        self.assertEqual(published_documents(tnu_html("Aposentadoria rural"), TNU), [])
        for invalid in [body.replace(b'id="900_1"', b'id="x"'),
                        body.replace(NUMBER.encode(), b"12345"), body.replace(b"</html>", body + b"</html>"),
                        tnu_html("BPC \ufffd")]:
            with self.assertRaises(ValueError):
                published_documents(invalid, TNU)

    def test_trf3_only_header_number(self):
        body = f'''<html><body><p>Recurso Nº {NUMBER}</p><p>R E L A T Ó R I O</p>
        <p>Benefício assistencial. Precedente 1053078-37.2022.4.01.3400.</p></body></html>'''.encode()
        row = published_documents(body, TRF3)[0]
        self.assertEqual(row["numeros_cnj"], [NUMBER])
        self.assertEqual(row["documento_id"], "123")
        with self.assertRaises(ValueError):
            published_documents(body.replace(b"R E L A T", b"x"), TRF3)

    def test_trf5_actual_cells_encoding_and_print_time_exclusion(self):
        body = f'''<html><meta charset="iso-8859-1"><td class="conteudo_body_content">
        <table><tr><td class="grid">Processo: {NUMBER}</td>
        <td class="grid">Data de Julgamento: 26/01/2023</td></tr></table>
        <b>Ementa</b>Benefício assistencial BPC<hr><b>Inteiro Teor</b><p>Voto publicado.</p>
        </td><p>Visualizado/Impresso em instante variável</p></html>'''.encode("latin-1")
        row = published_documents(body, TRF5)[0]
        self.assertEqual(row["ementa"], "Benefício assistencial BPC")
        self.assertEqual(row["data_decisao"].isoformat(), "2023-01-26")
        self.assertNotIn("Visualizado", row["texto"])
        self.assertEqual(row["numeros_cnj"], [NUMBER])
        with self.assertRaises(ValueError):
            published_documents(body.replace(b"Processo:", b"Outro:"), TRF5)

    def test_blocked_and_error_pages_are_not_empty_results(self):
        with self.assertRaises(SourceBlocked):
            published_documents(b'<html class="g-recaptcha">challenge</html>', TNU)
        for body in [b"not HTML", b"<html>Internal error</html>"]:
            with self.assertRaises(ValueError):
                published_documents(body, TNU)

    def test_trf5_legacy_number_is_preserved_without_inventing_cnj(self):
        body = b'''<html><td class="conteudo_body_content"><table><tr>
        <td class="grid">Processo: 2009.85.02.502275-8</td></tr></table>
        <b>Ementa</b>LOAS BPC<b>Inteiro Teor</b></td></html>'''
        row = published_documents(body, TRF5)[0]
        self.assertEqual(row["numero_origem"], "2009.85.02.502275-8")
        self.assertEqual(row["numeros_cnj"], [])
        self.assertIsNone(row["payload"]["numero_processo"])
        self.assertEqual(row["payload"]["formato_numero_origem"], "legado_sem_cnj")
        with self.assertRaises(ValueError):
            published_documents(body.replace(b"2009.85.02.502275-8", b"12345"), TRF5)

    def test_trf6_published_decision_full_text(self):
        body = f'''<html><head><title>Documento:60000591444</title></head><body><p>Documento:60000591444</p>
        <p>Poder Judiciario</p><p>PROCESSO {NUMBER}/TRF6</p><p>ACORDAO</p>
        <p>RELATORIO</p><p>Inteiro teor publico sobre BPC e beneficio assistencial e referencia ao precedente 5003019-04.2019.8.13.0396.</p></body></html>'''.encode("latin-1")
        row = published_documents(body, TRF6, expected_number=NUMBER)[0]
        self.assertEqual(row["tribunal"], "TRF6")
        self.assertEqual(row["documento_id"], "123")
        self.assertEqual(row["numeros_cnj"], [NUMBER])
        self.assertIn("beneficio assistencial", row["texto"])
        with self.assertRaises(ValueError):
            published_documents(body.replace(NUMBER.encode(), b"12345"), TRF6)
        with self.assertRaises(ValueError):
            published_documents(body, TRF6, expected_number="1053078-37.2022.4.01.3400")
        with self.assertRaises(ValueError):
            published_documents(body, TRF6, expected_number="5003019-04.2019.8.13.0396")

    def test_trf4_published_decision_validates_result_cnj_not_citations(self):
        body = f'''<html><head><title>Documento:40006078851</title></head><body>
        <p>Apelação Cível Nº {NUMBER}/RS</p><p>RELATÓRIO</p>
        <p>Benefício assistencial BPC. Cita o processo 1053078-37.2022.4.01.3400.</p>
        <p>VOTO</p><p>Inteiro teor publicado do TRF4.</p></body></html>'''.encode("latin-1")
        row = published_documents(body, TRF4, expected_number=NUMBER)[0]
        self.assertEqual(row["fonte"], "trf4_jurisprudencia")
        self.assertEqual(row["tribunal"], "TRF4")
        self.assertEqual(row["numeros_cnj"], [NUMBER])
        self.assertIn("Inteiro teor publicado", row["texto"])
        with self.assertRaises(ValueError):
            published_documents(body, TRF4, expected_number="1053078-37.2022.4.01.3400")
        with self.assertRaises(ValueError):
            published_documents(body.replace(NUMBER.encode(), b"12345"), TRF4, expected_number=NUMBER)

    def test_trf2_published_document_requires_card_number_in_header(self):
        number = "5001234-56.2025.4.02.5101"
        body = f'''<html><head><title>Documento:40001234567</title></head><body>
        <p>Apelação Cível Nº {number}/RJ</p><p>RELATÓRIO</p>
        <p>Benefício assistencial BPC; referência a {NUMBER} em citação.</p>
        <p>VOTO</p><p>Inteiro teor público da decisão.</p></body></html>'''.encode("latin-1")
        row = published_documents(body, TRF2, expected_number=number)[0]
        self.assertEqual(row["fonte"], "trf2_jurisprudencia")
        self.assertEqual(row["tribunal"], "TRF2")
        self.assertEqual(row["numeros_cnj"], [number])
        with self.assertRaises(ValueError):
            published_documents(body, TRF2, expected_number=NUMBER)

    def test_redirect_cannot_leave_official_https_origin(self):
        handler = OfficialRedirectHandler({"web.trf3.jus.br"})
        request = Request(TRF3)
        self.assertIsNotNone(handler.redirect_request(request, None, 302, "Found", {}, TRF3))
        for url in ["http://web.trf3.jus.br/a", "https://example.org/a", "https://user@web.trf3.jus.br/a"]:
            with self.assertRaises(ValueError):
                handler.redirect_request(request, None, 302, "Found", {}, url)

    def test_command_bronze_dedup_exact_link_and_failed_coleta(self):
        with tempfile.TemporaryDirectory() as work:
            db_url = "sqlite:///" + str(Path(work) / "base.sqlite")
            store = PostgresStore(db_url)
            Base.metadata.create_all(store.engine)
            with store.Session.begin() as session:
                session.add(Processo(numero_processo=NUMBER))
            store.close()
            args = SimpleNamespace(urls=[TNU], timeout=30, raw_dir=Path(work) / "raw")
            settings = Settings(database_url=db_url)
            with patch("bpc_ingestion.cli.PublicHttp") as client:
                client.return_value.fetch.return_value = tnu_html()
                collect_published_documents(args, settings)
                collect_published_documents(args, settings)
                client.return_value.fetch.side_effect = TimeoutError("network timeout")
                with self.assertRaises(RuntimeError):
                    collect_published_documents(args, settings)
            store = PostgresStore(db_url)
            try:
                with store.Session() as session:
                    self.assertEqual(len(list(session.scalars(select(DocumentoPublico)))), 1)
                    self.assertEqual(len(list(session.scalars(select(DocumentoProcesso)))), 1)
                    self.assertEqual(len(list(session.scalars(select(Processo)))), 1)
                    runs = list(session.scalars(select(Coleta)))
                    self.assertEqual(sorted(r.status for r in runs), ["concluida", "concluida", "falhou"])
                    for run in runs:
                        if run.arquivo_bruto:
                            with gzip.open(run.arquivo_bruto, "rb") as raw:
                                self.assertEqual(raw.read(), tnu_html())
            finally:
                store.close()
