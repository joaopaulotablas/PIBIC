"""Busca e pagina resultados no portal publico de jurisprudencia do TRF6."""
from __future__ import annotations

import math
import re
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup

from .public_sources import PublicHttp, cnj_number
from .published_documents import official_url

HOST = "eproc-jur.trf6.jus.br"
BASE = f"https://{HOST}/eproc/externo_controlador.php"
HOME = BASE + "?" + urlencode({"acao": "jurisprudencia@jurisprudencia/pesquisar"})
ORIGINS = ("TRF6", "TRU6", "Turmas Recursais", "Varas Federais")


def unique_links(links: list[str], seen: set[str]) -> list[str]:
    fresh = []
    for link in links:
        if link not in seen:
            seen.add(link)
            fresh.append(link)
    return fresh


def _route(value: str, action: str) -> str:
    target = urljoin(HOME, value)
    url = urlparse(target)
    if (url.scheme != "https" or url.hostname != HOST or url.port not in (None, 443)
            or url.username or url.password or url.fragment or url.path != "/eproc/externo_controlador.php"
            or parse_qs(url.query, keep_blank_values=True) != {"acao": ["jurisprudencia@jurisprudencia/" + action]}):
        raise ValueError("Rota de busca/paginacao TRF6 diferente da rota publica observada")
    return target


def _form_values(form) -> list[tuple[str, str]]:
    values = []
    for tag in form.find_all(["input", "select", "textarea"]):
        name, kind = tag.get("name"), tag.get("type", "text").lower()
        if kind == "password":
            raise ValueError("Formulario TRF6 exige credencial; coleta interrompida")
        if not name or tag.has_attr("disabled") or kind in {"submit", "button", "file", "reset"}:
            continue
        if kind in {"checkbox", "radio"} and not tag.has_attr("checked"):
            continue
        if tag.name == "select":
            options = tag.find_all("option")
            chosen = [o for o in options if o.has_attr("selected") and not o.has_attr("disabled")]
            if not chosen and not tag.has_attr("multiple") and options:
                chosen = [options[0]]
            values.extend((name, o.get("value", o.get_text())) for o in chosen)
        elif tag.name == "textarea":
            values.append((name, tag.get_text()))
        else:
            values.append((name, tag.get("value") or ("on" if kind in {"checkbox", "radio"} else "")))
    return values


def page_state(body: bytes, expected_page: int, size: int = 10) -> tuple[int, int, list[str]]:
    soup = BeautifulSoup(body, "html.parser")
    titles = [h.get_text(" ", strip=True) for h in soup.select("#divResultados h2")]
    total_inputs = soup.find_all("input", id="hdnTotalResultado")
    pages_inputs = soup.find_all("input", id="hdnTotalPaginas")
    current_inputs = soup.find_all("input", id="hdnPaginaAtual")
    if not (len(total_inputs) == len(pages_inputs) == len(current_inputs) == 1):
        raise ValueError("Metadados de paginação TRF6 ausentes/ambiguos")
    raw_total, raw_pages, raw_page = (x.get("value", "") for x in (total_inputs[0], pages_inputs[0], current_inputs[0]))
    cards = soup.select(".resultadoItem")
    empty_headers = [h for h in soup.select("#divResultados h2")
                     if h.get_text(" ", strip=True) == "0 documentos encontrados"]
    if (expected_page == 1 and len(empty_headers) == 1 and len(cards) == 0
            and raw_total == "" and raw_pages == "" and raw_page == "1"):
        return 0, 0, []
    if not all(re.fullmatch(r"\d{1,9}", value) for value in (raw_total, raw_pages, raw_page)):
        raise ValueError("Metadados numericos de paginação TRF6 inválidos")
    total, pages, current = int(raw_total), int(raw_pages), int(raw_page)
    expected_pages = math.ceil(total / size) if total else 0
    if pages != expected_pages or current != expected_page:
        raise ValueError("Pagina/total TRF6 diverge do tamanho de 10 itens")
    expected_count = min(size, max(0, total - (expected_page - 1) * size))
    if len(cards) != expected_count:
        raise ValueError("Pagina TRF6 incompleta ou layout alterado")
    links, ids = [], set()
    for card in cards:
        anchors = card.select("a.inteiroTeor[data-link]")
        if len(anchors) != 1:
            raise ValueError("Resultado TRF6 sem link publico unico de inteiro teor")
        source, identifier, canonical = official_url(urljoin(HOME, anchors[0]["data-link"]))
        if source != "trf6_jurisprudencia" or card.get("id") != "resultado" + identifier or identifier in ids:
            raise ValueError("Identidade/link TRF6 divergente ou repetido")
        ids.add(identifier)
        links.append(canonical)
    return pages, total, links


class Trf6SearchClient:
    def __init__(self, http: PublicHttp | None = None, on_response=None):
        self.http = http or PublicHttp(allowed_hosts={HOST}, max_bytes=24 * 1024 * 1024,
                                       form_encoding="iso-8859-1")
        self.on_response = on_response
        self.context = {}

    def process_numbers(self, body: bytes) -> dict[str, str]:
        return self._process_numbers(body)

    @staticmethod
    def _process_numbers(body: bytes) -> dict[str, str]:
        soup = BeautifulSoup(body, "html.parser")
        result = {}
        for card in soup.select(".resultadoItem"):
            doc_links = card.select("a.inteiroTeor[data-link]")
            process_links = card.select("a.numero-processo[href]")
            if len(doc_links) != 1 or len(process_links) != 1:
                raise ValueError("Resultado TRF6 sem links unicos de documento e processo")
            source, identifier, _ = official_url(urljoin(HOME, doc_links[0]["data-link"]))
            process_url = urlparse(process_links[0]["href"])
            query = parse_qs(process_url.query, keep_blank_values=True)
            eproc_process = (process_url.hostname == "eproc2g.trf6.jus.br"
                and process_url.path == "/eproc/externo_controlador.php"
                and set(query) == {"acao", "acao_origem", "acao_retorno", "num_processo"}
                and query.get("acao") == ["processo_seleciona_publica"]
                and query.get("acao_origem") == ["processo_consulta_publica"]
                and query.get("acao_retorno") == ["processo_consulta_publica"]
                and len(query.get("num_processo", [])) == 1)
            pje_process = (process_url.hostname == "pje1g.trf6.jus.br"
                and process_url.path == "/consultapublica/ConsultaPublica/listView.seam"
                and set(query) == {"numeroProcesso"} and len(query.get("numeroProcesso", [])) == 1)
            digits = query.get("num_processo", []) if eproc_process else query.get("numeroProcesso", [])
            if (source != "trf6_jurisprudencia" or process_url.scheme != "https"
                    or process_url.username or process_url.password or process_url.fragment
                    or not (eproc_process or pje_process)
                    or len(digits) != 1 or cnj_number(digits[0]) is None or identifier in result):
                raise ValueError("Identidade de processo TRF6 ausente/ambigua no resultado publicado")
            result[identifier] = cnj_number(digits[0])
        return result

    def fetch(self, url, data=None):
        body = self.http.fetch(url, data)
        if self.on_response:
            self.on_response(url, body)
        return body

    def pages(self, query: str, limit: int = 5, origins: tuple[str, ...] = ("TRF6",),
              start_page: int = 1):
        if (not query.strip() or len(query) > 200 or not 1 <= limit <= 100
                or not 1 <= start_page <= 1_000_000):
            raise ValueError("Use consulta TRF6 nao vazia ate 200 caracteres, 1..100 paginas e pagina inicial positiva")
        if not origins or len(set(origins)) != len(origins) or any(origin not in ORIGINS for origin in origins):
            raise ValueError("Origem TRF6 deve ser selecionada entre as opcoes publicadas no formulario")
        home = BeautifulSoup(self.fetch(HOME), "html.parser")
        forms = home.find_all("form", id="frmJurisprudenciaPesquisa")
        if (len(forms) != 1 or forms[0].get("method", "").lower() != "post"
                or not forms[0].find("input", attrs={"name": "txtPesquisa"})):
            raise ValueError("Formulario publico de pesquisa TRF6 ausente/alterado")
        form = forms[0]
        options = form.select("#selOrigem option")
        origin_values = {}
        for origin in origins:
            matches = [o.get("value") for o in options if o.get("value") and o.get_text(" ", strip=True) == origin]
            if len(matches) != 1:
                raise ValueError(f"Origem {origin} nao identificada unicamente no formulario TRF6")
            origin_values[origin] = matches[0]
        overrides = {"txtPesquisa", "selOrigem[]", "rdoCampo", "chkAgruparResultados"}
        data = [(key, value) for key, value in _form_values(form) if key not in overrides]
        data.extend([("txtPesquisa", query), *(('selOrigem[]', origin_values[x]) for x in origins),
                     ("rdoCampo", "I"), ("chkAgruparResultados", "on")])
        body = self.fetch(_route(form.get("action", ""), "listar_resultados"), data)
        pages, total, links = page_state(body, 1)
        self.last_process_numbers = self._process_numbers(body)
        soup = BeautifulSoup(body, "html.parser")
        result_forms = soup.find_all("form", id="frmJurisprudenciaResultado")
        pager = soup.find_all("input", id="hdnUrlPaginar")
        if len(result_forms) != 1 or len(pager) != 1:
            raise ValueError("Formulario de resultados/paginacao TRF6 ausente ou ambiguo")
        target = _route(pager[0].get("value", ""), "ajax_paginar_resultado")
        fields = _form_values(result_forms[0])
        values = dict(fields)
        if values.get("selTamanhoPagina") != "10":
            raise ValueError("Tamanho de pagina TRF6 diferente de 10")
        self.context = {"origens": list(origins), "origens_valores": [origin_values[origin] for origin in origins],
                        "campo_pesquisa": "I", "agrupar_resultados": True, "itens_pagina": 10,
                        "resultados_informados": total, "paginas_informadas": pages,
                        "versao_busca": "trf6_eproc_form_v1", "pagina_inicial": start_page}
        if start_page == 1:
            yield 1, body, links
        first_page = max(2, start_page)
        last_page = min(start_page + limit - 1, pages)
        for page in range(first_page, last_page + 1):
            data = [(key, str(page) if key == "hdnPaginaAtual" else value) for key, value in fields]
            body = self.fetch(target, data)
            new_pages, new_total, links = page_state(body, page)
            if (new_pages, new_total) != (pages, total):
                raise ValueError("Total de resultados TRF6 mudou durante a paginacao")
            self.last_process_numbers = self._process_numbers(body)
            yield page, body, links
