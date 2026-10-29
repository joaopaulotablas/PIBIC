import unittest
from unittest.mock import Mock

from bpc_ingestion.trf4_search import Trf4SearchClient, page_state


def result_page(page, entries, total=11):
    cards = []
    for identifier, number in entries:
        digits = "".join(c for c in number if c.isdigit())
        cards.append(f'''<div class="resultadoItem" id="resultado{identifier}">
        <a class="inteiroTeor" data-link="externo_controlador.php?acao=jurisprudencia@jurisprudencia/download_inteiro_teor&amp;id_jurisprudencia={identifier}&amp;termosPesquisados=YnBj"></a>
        <a class="numero-processo" href="http://www.trf4.jus.br/trf4/processos/acompanhamento/resultado_pesquisa.php?selForma=NU&amp;selOrigem=TRF&amp;txtValor={digits}">{number}/TRF4</a></div>''')
    return f'''<html><div id="divResultados">{''.join(cards)}</div>
    <form id="frmJurisprudenciaResultado" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
    <input type="hidden" name="hdnUrlPaginar" id="hdnUrlPaginar" value="externo_controlador.php?acao=jurisprudencia@jurisprudencia/ajax_paginar_resultado">
    <input type="hidden" name="hdnTotalPaginas" id="hdnTotalPaginas" value="{(total + 9) // 10}"><input type="hidden" name="hdnTotalResultado" id="hdnTotalResultado" value="{total}">
    <input type="hidden" name="hdnPaginaAtual" id="hdnPaginaAtual" value="{page}"></form></html>'''.encode()


class Trf4SearchTest(unittest.TestCase):
    def test_validates_public_cards_and_case_identity(self):
        number = "5006875-14.2022.4.04.7005"
        html = result_page(1, [("41791387746332728992135093329", number)], total=1)
        pages, total, links, identities = page_state(html, 1)
        self.assertEqual((pages, total), (1, 1))
        self.assertEqual(identities, {"41791387746332728992135093329": number})
        self.assertNotIn("termosPesquisados", links[0])

    def test_rejects_fake_or_inconsistent_result_pages(self):
        valid = result_page(1, [("41791387746332728992135093329", "5006875-14.2022.4.04.7005")])
        for body in [valid.replace(b"id=\"resultado417", b"id=\"resultado999"),
                     valid.replace(b"hdnPaginaAtual\" value=\"1", b"hdnPaginaAtual\" value=\"2"),
                     valid.replace(b"txtValor=50068751420224047005", b"txtValor=10530783720224013400")]:
            with self.subTest(body=body[:80]), self.assertRaises(ValueError):
                page_state(body, 1)

    def test_search_uses_session_and_paginates_form_state(self):
        number = "5006875-14.2022.4.04.7005"
        identifier = "41791387746332728992135093329"
        home = b'''<form id="frmJurisprudenciaPesquisa" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
        <input name="txtPesquisa"><select id="selOrigem" name="selOrigem[]"><option value="1" selected>TRF4</option></select>
        <input type="radio" name="rdoCampo" value="I" checked><input type="checkbox" name="chkAgruparResultados" checked></form>'''
        page1 = result_page(1, [(f"{int(identifier)+i}", number) for i in range(10)])
        page2 = result_page(2, [(f"{int(identifier)+10}", number)], total=11)
        http = Mock()
        http.fetch.side_effect = [home, page1, page2]
        client = Trf4SearchClient(http)
        pages = list(client.pages("BPC", limit=2))
        self.assertEqual([page[0] for page in pages], [1, 2])
        self.assertEqual(len(pages[0][2]), 10)
        self.assertEqual(len(pages[1][2]), 1)
        self.assertEqual(http.fetch.call_count, 3)

    def test_search_can_resume_at_later_page(self):
        number = "5006875-14.2022.4.04.7005"
        identifier = "41791387746332728992135093329"
        home = b'''<form id="frmJurisprudenciaPesquisa" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
        <input name="txtPesquisa"><select id="selOrigem" name="selOrigem[]"><option value="1" selected>TRF4</option></select>
        <input type="radio" name="rdoCampo" value="I" checked><input type="checkbox" name="chkAgruparResultados" checked></form>'''
        page1 = result_page(1, [(f"{int(identifier)+i}", number) for i in range(10)])
        page2 = result_page(2, [(f"{int(identifier)+10}", number)], total=11)
        http = Mock()
        http.fetch.side_effect = [home, page1, page2]
        client = Trf4SearchClient(http)

        pages = list(client.pages("BPC", limit=1, start_page=2))

        self.assertEqual([page[0] for page in pages], [2])
        self.assertEqual(len(pages[0][2]), 1)
        self.assertEqual(client.context["pagina_inicial"], 2)
        self.assertEqual(http.fetch.call_count, 3)


if __name__ == "__main__":
    unittest.main()
