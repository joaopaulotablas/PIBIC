import unittest
from unittest.mock import Mock

from bpc_ingestion.trf6_search import Trf6SearchClient, page_state, unique_links


def result_page(page, entries, total=11, pages=2):
    cards = []
    for identifier, digits in entries:
        cards.append(f'''<div class="resultadoItem" id="resultado{identifier}">
        <a class="inteiroTeor" data-link="externo_controlador.php?acao=jurisprudencia@jurisprudencia/download_inteiro_teor&amp;id_jurisprudencia={identifier}"></a>
        <a class="numero-processo" href="https://eproc2g.trf6.jus.br/eproc/externo_controlador.php?acao=processo_seleciona_publica&amp;acao_origem=processo_consulta_publica&amp;acao_retorno=processo_consulta_publica&amp;num_processo={digits}"></a></div>''')
    return f'''<html><div id="divResultados">{''.join(cards)}</div>
    <form id="frmJurisprudenciaResultado" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
    <input name="hdnUrlPaginar" id="hdnUrlPaginar" value="externo_controlador.php?acao=jurisprudencia@jurisprudencia/ajax_paginar_resultado">
    <input name="hdnTotalPaginas" id="hdnTotalPaginas" value="{pages}"><input name="hdnTotalResultado" id="hdnTotalResultado" value="{total}">
    <input name="hdnPaginaAtual" id="hdnPaginaAtual" value="{page}"><select name="selTamanhoPagina"><option value="10" selected>10</option></select>
    </form></html>'''.encode()


class Trf6SearchTest(unittest.TestCase):
    def test_validates_page_metadata_and_published_links(self):
        html = b'''<html><div id="divResultados"><h2>1 documentos encontrados</h2>
        <div class="resultadoItem" id="resultado123"><a class="inteiroTeor" data-link="externo_controlador.php?acao=jurisprudencia@jurisprudencia/download_inteiro_teor&amp;id_jurisprudencia=123&amp;termosPesquisados=Ynpj"></a></div>
        </div><input id="hdnTotalResultado" value="1"><input id="hdnTotalPaginas" value="1"><input id="hdnPaginaAtual" value="1"></html>'''
        pages, total, links = page_state(html, 1)
        self.assertEqual((pages, total), (1, 1))
        self.assertIn("id_jurisprudencia=123", links[0])
        self.assertNotIn("termosPesquisados", links[0])

    def test_rejects_inconsistent_counts_or_fake_empty(self):
        for html in [
            b'<html><input id="hdnTotalResultado" value="10"><input id="hdnTotalPaginas" value="1"><input id="hdnPaginaAtual" value="2"></html>',
            b'<html><input id="hdnTotalResultado" value="0"><input id="hdnTotalPaginas" value="0"><input id="hdnPaginaAtual" value="1"><div class="resultadoItem"></div></html>',
        ]:
            with self.subTest(html=html), self.assertRaises(ValueError):
                page_state(html, 1)

    def test_accepts_only_portal_explicit_empty_result(self):
        html = b'''<html><div id="divResultados"><h2>0 documentos encontrados</h2></div>
        <input id="hdnTotalResultado"><input id="hdnTotalPaginas"><input id="hdnPaginaAtual" value="1"></html>'''
        self.assertEqual(page_state(html, 1), (0, 0, []))
        with self.assertRaises(ValueError):
            page_state(html.replace(b"0 documentos encontrados", b"Busca concluida"), 1)

    def test_search_pages_extract_process_identity_and_dedupe_documents(self):
        home = b'''<form id="frmJurisprudenciaPesquisa" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
        <input name="txtPesquisa"><select id="selOrigem" name="selOrigem[]"><option value="1" selected>TRF6</option></select>
        <input type="radio" name="rdoCampo" value="I" checked><input type="checkbox" name="chkAgruparResultados" checked>
        </form>'''
        entries = [(i, f"{i:020d}") for i in range(101, 111)]
        http = Mock()
        http.fetch.side_effect = [home, result_page(1, entries), result_page(2, entries[:1])]
        client = Trf6SearchClient(http)
        pages = list(client.pages("BPC", limit=2))
        self.assertEqual([p[0] for p in pages], [1, 2])
        self.assertEqual(len(pages[0][2]), 10)
        self.assertEqual(len(pages[1][2]), 1)
        self.assertEqual(len(client.process_numbers(pages[0][1])), 10)
        seen = set()
        self.assertEqual(len(unique_links(pages[0][2], seen)), 10)
        self.assertEqual(unique_links(pages[1][2], seen), [])
        self.assertEqual(http.fetch.call_count, 3)

    def test_search_pages_can_resume_at_requested_page(self):
        home = b'''<form id="frmJurisprudenciaPesquisa" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
        <input name="txtPesquisa"><select id="selOrigem" name="selOrigem[]"><option value="1" selected>TRF6</option></select>
        <input type="radio" name="rdoCampo" value="I" checked><input type="checkbox" name="chkAgruparResultados" checked>
        </form>'''
        entries = [(i, f"{i:020d}") for i in range(101, 111)]
        http = Mock()
        http.fetch.side_effect = [home, result_page(1, entries, total=31, pages=4),
                                  result_page(3, entries, total=31, pages=4),
                                  result_page(4, entries[:1], total=31, pages=4)]
        client = Trf6SearchClient(http)
        pages = list(client.pages("BPC", limit=2, start_page=3))
        self.assertEqual([p[0] for p in pages], [3, 4])
        self.assertEqual(http.fetch.call_count, 4)

    def test_turmas_recursais_search_uses_published_pje_case_link(self):
        identifier = "381790945806795290566943197896"
        number = "50068751420224047005"
        html = f'''<div class="resultadoItem" id="resultado{identifier}">
        <a class="inteiroTeor" data-link="externo_controlador.php?acao=jurisprudencia@jurisprudencia/download_inteiro_teor&amp;id_jurisprudencia={identifier}"></a>
        <a class="numero-processo" href="https://pje1g.trf6.jus.br/consultapublica/ConsultaPublica/listView.seam?numeroProcesso={number}"></a></div>'''.encode()
        self.assertEqual(Trf6SearchClient._process_numbers(html), {identifier: "5006875-14.2022.4.04.7005"})


if __name__ == "__main__":
    unittest.main()
