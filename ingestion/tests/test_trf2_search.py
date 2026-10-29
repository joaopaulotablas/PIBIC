import unittest
from unittest.mock import Mock

from bpc_ingestion.trf2_search import Trf2SearchClient, page_state


def result_page(page, entries, total=11):
    cards = []
    for identifier, number in entries:
        digits = "".join(c for c in number if c.isdigit())
        cards.append(f'''<div class="resultadoItem" id="resultado{identifier}">
        <a class="inteiroTeor" data-link="externo_controlador.php?acao=jurisprudencia@jurisprudencia/download_inteiro_teor&amp;id_jurisprudencia={identifier}&amp;termosPesquisados=QnBj"></a>
        <a class="numero-processo" href="https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=processo_seleciona_publica&amp;acao_origem=processo_consulta_publica&amp;acao_retorno=processo_consulta_publica&amp;num_processo={digits}">{number}/TRF2</a></div>''')
    return f'''<html><div id="divResultados">{''.join(cards)}</div>
    <form id="frmJurisprudenciaResultado" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
    <input type="hidden" name="hdnUrlPaginar" id="hdnUrlPaginar" value="externo_controlador.php?acao=jurisprudencia@jurisprudencia/ajax_paginar_resultado">
    <input type="hidden" name="hdnTotalPaginas" id="hdnTotalPaginas" value="{(total + 9) // 10}"><input type="hidden" name="hdnTotalResultado" id="hdnTotalResultado" value="{total}">
    <input type="hidden" name="hdnPaginaAtual" id="hdnPaginaAtual" value="{page}"></form></html>'''.encode()


class Trf2SearchTest(unittest.TestCase):
    def test_validates_public_document_and_case_identity(self):
        number = "5006875-14.2022.4.02.7005"
        identifier = "21787912823627697229862470536"
        pages, total, links, numbers = page_state(result_page(1, [(identifier, number)], total=1), 1)
        self.assertEqual((pages, total), (1, 1))
        self.assertEqual(numbers, {identifier: number})
        self.assertEqual(len(links), 1)

    def test_rejects_changed_document_identity_or_case_number(self):
        valid = result_page(1, [("21787912823627697229862470536", "5006875-14.2022.4.04.7005")], total=1)
        for body in [valid.replace(b"id=\"resultado217", b"id=\"resultado999"),
                     valid.replace(b"num_processo=50068751420224047005", b"num_processo=10530783720224013400"),
                     valid.replace(b"hdnPaginaAtual\" value=\"1", b"hdnPaginaAtual\" value=\"2")]:
            with self.subTest(body=body[:80]), self.assertRaises(ValueError):
                page_state(body, 1)

    def test_accepts_official_jfes_case_link_for_turmas_recursais(self):
        body = result_page(1, [("21787912823627697229862470536", "5006875-14.2022.4.02.7005")], total=1)
        body = body.replace(b"eproc.trf2.jus.br", b"eproc.jfes.jus.br")
        self.assertEqual(len(page_state(body, 1)[2]), 1)

    def test_search_preserves_form_session_and_paginates(self):
        number = "5006875-14.2022.4.02.7005"
        home = b'''<form id="frmJurisprudenciaPesquisa" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
        <input name="txtPesquisa"><select id="selOrigem" name="selOrigem[]"><option value="1" selected>TRF2</option></select>
        <input type="radio" name="rdoCampo" value="I" checked><input type="checkbox" name="chkAgruparResultados" checked></form>'''
        start = 21787912823627697229862470536
        page1 = result_page(1, [(str(start + i), number) for i in range(10)])
        page2 = result_page(2, [(str(start + 10), number)])
        http = Mock()
        http.fetch.side_effect = [home, page1, page2]
        client = Trf2SearchClient(http)
        pages = list(client.pages("BPC", limit=2))
        self.assertEqual([page[0] for page in pages], [1, 2])
        self.assertEqual(len(pages[0][2]), 10)
        self.assertEqual(len(pages[1][2]), 1)
        self.assertEqual(http.fetch.call_count, 3)

    def test_search_can_resume_at_later_page(self):
        number = "5006875-14.2022.4.02.7005"
        home = b'''<form id="frmJurisprudenciaPesquisa" method="post" action="externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados">
        <input name="txtPesquisa"><select id="selOrigem" name="selOrigem[]"><option value="1" selected>TRF2</option></select>
        <input type="radio" name="rdoCampo" value="I" checked><input type="checkbox" name="chkAgruparResultados" checked></form>'''
        start = 21787912823627697229862470536
        page1 = result_page(1, [(str(start + i), number) for i in range(10)])
        page2 = result_page(2, [(str(start + 10), number)])
        http = Mock()
        http.fetch.side_effect = [home, page1, page2]
        client = Trf2SearchClient(http)

        pages = list(client.pages("BPC", limit=1, start_page=2))

        self.assertEqual([page[0] for page in pages], [2])
        self.assertEqual(len(pages[0][2]), 1)
        self.assertEqual(client.context["pagina_inicial"], 2)
        self.assertEqual(http.fetch.call_count, 3)


if __name__ == "__main__":
    unittest.main()
