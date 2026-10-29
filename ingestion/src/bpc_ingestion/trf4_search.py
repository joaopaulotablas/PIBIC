"""Busca e pagina documentos publicos de jurisprudencia do eproc/TRF4."""
from __future__ import annotations

import math
import re
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

from bs4 import BeautifulSoup

from .public_sources import PublicHttp, cnj_number
from .published_documents import official_url

HOST = "jurisprudencia.trf4.jus.br"
BASE = f"https://{HOST}/eproc2trf4/externo_controlador.php"
HOME = BASE + "?" + urlencode({"acao": "jurisprudencia@jurisprudencia/pesquisar"})
ORIGINS = ("TRF4", "TRU4", "Turmas Recursais")
PAGE_SIZE = 10


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
    expected = "jurisprudencia@jurisprudencia/" + action
    if (url.scheme != "https" or url.hostname != HOST or url.port not in (None, 443)
            or url.username or url.password or url.fragment
            or url.path != "/eproc2trf4/externo_controlador.php"
            or parse_qs(url.query, keep_blank_values=True) != {"acao": [expected]}):
        raise ValueError("Rota de busca/paginacao TRF4 diferente da rota publica observada")
    return target


def _form_values(form) -> list[tuple[str, str]]:
    values = []
    for tag in form.find_all(["input", "select", "textarea"]):
        name, kind = tag.get("name"), tag.get("type", "text").lower()
        if kind == "password":
            raise ValueError("Formulario TRF4 exige credencial; coleta interrompida")
        if not name or tag.has_attr("disabled") or kind in {"submit", "button", "file", "reset"}:
            continue
        if kind in {"checkbox", "radio"} and not tag.has_attr("checked"):
            continue
        if tag.name == "select":
            options = tag.find_all("option")
            chosen = [option for option in options if option.has_attr("selected") and not option.has_attr("disabled")]
            if not chosen and not tag.has_attr("multiple") and options:
                chosen = [options[0]]
            values.extend((name, option.get("value", option.get_text())) for option in chosen)
        elif tag.name == "textarea":
            values.append((name, tag.get_text()))
        else:
            values.append((name, tag.get("value") or ("on" if kind in {"checkbox", "radio"} else "")))
    return values


def _card_id(card, anchor) -> tuple[str, str]:
    source, identifier, canonical = official_url(urljoin(HOME, anchor["data-link"]))
    if source != "trf4_jurisprudencia" or card.get("id") != "resultado" + identifier:
        raise ValueError("Identidade/link TRF4 divergente no resultado publicado")
    return identifier, canonical


def page_state(body: bytes, expected_page: int) -> tuple[int, int, list[str], dict[str, str]]:
    soup = BeautifulSoup(body, "html.parser")
    cards = soup.select(".resultadoItem")
    total_nodes = soup.select("input#hdnTotalResultado")
    pages_nodes = soup.select("input#hdnTotalPaginas")
    current_nodes = soup.select("input#hdnPaginaAtual")
    if not (len(total_nodes) == len(pages_nodes) == len(current_nodes) == 1):
        raise ValueError("Metadados de paginacao TRF4 ausentes ou ambiguos")
    raw_total, raw_pages, raw_current = (node.get("value", "") for node in
                                         (total_nodes[0], pages_nodes[0], current_nodes[0]))
    if not all(re.fullmatch(r"\d{1,9}", value) for value in (raw_total, raw_pages, raw_current)):
        raise ValueError("Metadados numericos de paginacao TRF4 invalidos")
    total, pages, current = int(raw_total), int(raw_pages), int(raw_current)
    if pages != (math.ceil(total / PAGE_SIZE) if total else 0) or current != expected_page:
        raise ValueError("Pagina/total TRF4 diverge do tamanho de 10 itens")
    expected_count = min(PAGE_SIZE, max(0, total - (expected_page - 1) * PAGE_SIZE))
    if len(cards) != expected_count:
        raise ValueError("Pagina TRF4 incompleta ou layout alterado")
    links, process_numbers, identifiers = [], {}, set()
    for card in cards:
        docs = card.select("a.inteiroTeor[data-link]")
        processes = card.select("a.numero-processo[href]")
        if len(docs) != 1 or len(processes) != 1:
            raise ValueError("Resultado TRF4 sem links unicos de documento e processo")
        identifier, canonical = _card_id(card, docs[0])
        process_url = urlparse(processes[0]["href"])
        query = parse_qs(process_url.query, keep_blank_values=True)
        raw = query.get("txtValor", [])
        display = re.search(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}",
                            processes[0].get_text(" ", strip=True))
        number = cnj_number(display.group(0)) if display else None
        if (identifier in identifiers or number is None or len(raw) != 1
                or cnj_number(raw[0]) != number
                or process_url.hostname != "www.trf4.jus.br"
                or process_url.path != "/trf4/processos/acompanhamento/resultado_pesquisa.php"
                or set(query) != {"selForma", "selOrigem", "txtValor"}
                or query.get("selForma") != ["NU"] or query.get("selOrigem", [""])[0] not in {"TRF", "RS", "PR", "SC"}):
            raise ValueError("CNJ/link de processo TRF4 ausente, divergente ou ambiguo")
        identifiers.add(identifier)
        process_numbers[identifier] = number
        links.append(canonical)
    return pages, total, links, process_numbers


class Trf4SearchClient:
    def __init__(self, http: PublicHttp | None = None, on_response=None):
        self.http = http or PublicHttp(allowed_hosts={HOST}, max_bytes=32 * 1024 * 1024,
                                       form_encoding="iso-8859-1")
        self.on_response = on_response
        self.context = {}
        self.last_process_numbers: dict[str, str] = {}

    def fetch(self, url, data=None, headers=None):
        body = self.http.fetch(url, data, headers=headers)
        if self.on_response:
            self.on_response(url, body)
        return body

    def pages(self, query: str, limit: int = 5, origins: tuple[str, ...] = ("TRF4",),
              start_page: int = 1):
        if (not query.strip() or len(query) > 200 or not 1 <= limit <= 100
                or not 1 <= start_page <= 1_000_000):
            raise ValueError("Use consulta TRF4 nao vazia ate 200 caracteres, 1..100 paginas e pagina inicial positiva")
        if not origins or len(set(origins)) != len(origins) or any(origin not in ORIGINS for origin in origins):
            raise ValueError("Origem deve ser TRF4, TRU4 ou Turmas Recursais conforme formulario")
        home = BeautifulSoup(self.fetch(HOME), "html.parser")
        forms = home.find_all("form", id="frmJurisprudenciaPesquisa")
        if len(forms) != 1 or forms[0].get("method", "").lower() != "post":
            raise ValueError("Formulario publico TRF4 ausente ou alterado")
        form = forms[0]
        options = form.select("#selOrigem option")
        selected = {}
        for origin in origins:
            found = [option.get("value") for option in options
                     if option.get("value") and option.get_text(" ", strip=True) == origin]
            if len(found) != 1:
                raise ValueError(f"Origem {origin} nao identificada unicamente no formulario TRF4")
            selected[origin] = found[0]
        overrides = {"txtPesquisa", "selOrigem[]", "rdoCampo", "chkAgruparResultados"}
        data = [(key, value) for key, value in _form_values(form) if key not in overrides]
        data.extend([("txtPesquisa", query), *(('selOrigem[]', selected[x]) for x in origins),
                     ("rdoCampo", "I"), ("chkAgruparResultados", "on")])
        body = self.fetch(_route(form.get("action", ""), "listar_resultados"), data,
                          headers={"Referer": HOME})
        pages, total, links, self.last_process_numbers = page_state(body, 1)
        results = BeautifulSoup(body, "html.parser").find_all("form", id="frmJurisprudenciaResultado")
        pagers = BeautifulSoup(body, "html.parser").select("input#hdnUrlPaginar")
        if len(results) != 1 or len(pagers) != 1:
            raise ValueError("Formulario de resultados/paginacao TRF4 ausente ou ambiguo")
        target = _route(pagers[0].get("value", ""), "ajax_paginar_resultado")
        fields = _form_values(results[0])
        self.context = {"origens": list(origins), "origens_valores": [selected[x] for x in origins],
                        "campo_pesquisa": "I", "itens_pagina": PAGE_SIZE,
                        "resultados_informados": total, "paginas_informadas": pages,
                        "versao_busca": "trf4_eproc_form_v1", "pagina_inicial": start_page}
        if start_page == 1:
            yield 1, body, links
        first_page = max(2, start_page)
        last_page = min(start_page + limit - 1, pages)
        for page in range(first_page, last_page + 1):
            data = [(key, str(page) if key == "hdnPaginaAtual" else value) for key, value in fields]
            body = self.fetch(target, data, headers={"Referer": target})
            new_pages, new_total, links, self.last_process_numbers = page_state(body, page)
            if (new_pages, new_total) != (pages, total):
                raise ValueError("Total de resultados TRF4 mudou durante a paginacao")
            yield page, body, links
