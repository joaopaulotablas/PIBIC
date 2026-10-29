"""Documentos HTML oficiais indicados por URL; não consulta autos nem inventa IDs."""
from __future__ import annotations

import re
from urllib.parse import parse_qs, urlencode, urlparse

from bs4 import BeautifulSoup

from .public_sources import bpc_text, check_blocked, cnj_number, public_date


CNJ = r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"


def official_url(value: str) -> tuple[str, str, str]:
    """Whitelist actual public document routes and canonicalize their identities."""
    url = urlparse(value)
    if (url.scheme != "https" or url.port not in (None, 443) or url.username
            or url.password or url.fragment):
        raise ValueError("URL de documento deve ser HTTPS oficial, sem credencial ou fragmento")
    query = parse_qs(url.query, keep_blank_values=True)
    if any(len(v) != 1 for v in query.values()):
        raise ValueError("Parâmetro repetido na URL de documento")
    if url.hostname == "eproctnu-jur.cjf.jus.br" and url.path == "/eproc/externo_controlador.php":
        action = "jurisprudencia@jurisprudencia/download_inteiro_teor"
        identifier = query.get("id_jurisprudencia", [""])[0]
        if set(query) != {"acao", "id_jurisprudencia"} or query["acao"] != [action] or not re.fullmatch(r"\d{1,100}", identifier):
            raise ValueError("URL TNU não é download público de jurisprudência reconhecido")
        return "tnu", identifier, f"https://{url.hostname}{url.path}?{urlencode({'acao': action, 'id_jurisprudencia': identifier})}"
    if url.hostname == "web.trf3.jus.br" and not query:
        match = re.fullmatch(r"/acordaos/Acordao/BuscarDocumentoPje/(\d{1,100})", url.path)
        if match:
            return "trf3_jurisprudencia", match[1], f"https://{url.hostname}{url.path}"
    if url.hostname == "jurisprudencia.trf5.jus.br" and url.path == "/jurisprudencia/exibir.wsp":
        identifier = query.get("tmp.id_documento", [""])[0]
        if set(query) == {"tmp.id_documento"} and re.fullmatch(r"\d{1,100}", identifier):
            return "trf5_jurisprudencia", identifier, f"https://{url.hostname}{url.path}?{urlencode({'tmp.id_documento': identifier})}"
    if url.hostname == "eproc-jur.trf6.jus.br" and url.path == "/eproc/externo_controlador.php":
        action = "jurisprudencia@jurisprudencia/download_inteiro_teor"
        identifier = query.get("id_jurisprudencia", [""])[0]
        if set(query) <= {"acao", "id_jurisprudencia", "termosPesquisados"} and query.get("acao") == [action] and re.fullmatch(r"\d{1,100}", identifier):
            highlight = query.get("termosPesquisados")
            if highlight is not None:
                import base64
                if len(highlight) != 1 or len(highlight[0]) > 2048:
                    raise ValueError("Realce TRF6 invÃ¡lido")
                try:
                    base64.b64decode(highlight[0], validate=True)
                except ValueError as exc:
                    raise ValueError("Realce TRF6 nÃ£o Ã© base64 vÃ¡lido") from exc
            canonical = f"https://{url.hostname}{url.path}?{urlencode({'acao': action, 'id_jurisprudencia': identifier})}"
            return "trf6_jurisprudencia", identifier, canonical
    if url.hostname == "jurisprudencia.trf4.jus.br" and url.path == "/eproc2trf4/externo_controlador.php":
        action = "jurisprudencia@jurisprudencia/download_inteiro_teor"
        identifier = query.get("id_jurisprudencia", [""])[0]
        if (set(query) <= {"acao", "id_jurisprudencia", "termosPesquisados"}
                and query.get("acao") == [action] and re.fullmatch(r"\d{1,100}", identifier)):
            highlight = query.get("termosPesquisados")
            if highlight is not None:
                import base64
                if len(highlight) != 1 or len(highlight[0]) > 2048:
                    raise ValueError("Realce TRF4 invalido")
                try:
                    base64.b64decode(highlight[0], validate=True)
                except ValueError as exc:
                    raise ValueError("Realce TRF4 nao e base64 valido") from exc
            canonical = f"https://{url.hostname}{url.path}?{urlencode({'acao': action, 'id_jurisprudencia': identifier})}"
            return "trf4_jurisprudencia", identifier, canonical
    if url.hostname == "eproc.trf2.jus.br" and url.path == "/eproc/externo_controlador.php":
        action = "jurisprudencia@jurisprudencia/download_inteiro_teor"
        identifier = query.get("id_jurisprudencia", [""])[0]
        if (set(query) <= {"acao", "id_jurisprudencia", "termosPesquisados"}
                and query.get("acao") == [action] and re.fullmatch(r"\d{1,100}", identifier)):
            highlight = query.get("termosPesquisados")
            if highlight is not None:
                import base64
                if len(highlight) != 1 or len(highlight[0]) > 2048:
                    raise ValueError("Realce TRF2 invalido")
                try:
                    base64.b64decode(highlight[0], validate=True)
                except ValueError as exc:
                    raise ValueError("Realce TRF2 nao e base64 valido") from exc
            canonical = f"https://{url.hostname}{url.path}?{urlencode({'acao': action, 'id_jurisprudencia': identifier})}"
            return "trf2_jurisprudencia", identifier, canonical
    raise ValueError("URL fora das rotas públicas TNU/TRF2/TRF3/TRF4/TRF5/TRF6 permitidas")


def _number(text: str) -> str:
    numbers = {cnj_number(m) for m in re.findall(CNJ, text)}
    if len(numbers) != 1:
        raise ValueError("Cabeçalho não identifica um único CNJ completo")
    return numbers.pop()


def _document(source, identifier, url, number, text, kind, *, ementa=None, decision_date=None):
    if not text.strip() or "\ufffd" in text:
        raise ValueError("Documento vazio ou com perda de encoding")
    cnj = cnj_number(number)
    payload = {"id": identifier, "numero_processo": cnj, "texto": text,
               "tipo_documento": kind, "ementa": ementa,
               "data_decisao": decision_date.isoformat() if decision_date else None,
               "extracao_texto": "html_publicado", "versao_parser": "publicados_html_v1"}
    if cnj is None:
        payload.update(numero_origem=number, formato_numero_origem="legado_sem_cnj")
    return {"fonte": source, "documento_id": identifier,
            "tribunal": {"tnu": "TNU", "trf2_jurisprudencia": "TRF2", "trf3_jurisprudencia": "TRF3",
                         "trf4_jurisprudencia": "TRF4",
                         "trf5_jurisprudencia": "TRF5", "trf6_jurisprudencia": "TRF6"}[source],
            "tipo_documento": kind, "numero_origem": number, "numeros_cnj": [cnj] if cnj else [],
            "texto": text, "ementa": ementa, "decisao": None,
            "data_decisao": decision_date, "data_publicacao": None,
            "url_origem": url, "recurso_url": url,
            "payload": payload}


def published_documents(body: bytes, url: str, expected_number: str | None = None) -> list[dict]:
    source, identifier, canonical = official_url(url)
    check_blocked(body.decode("utf-8", errors="replace"))
    if not body.lstrip().startswith(b"<"):
        raise ValueError("Fonte não retornou HTML publicado")
    soup = BeautifulSoup(body, "html.parser")
    for tag in soup.find_all(["script", "style", "noscript"]):
        tag.decompose()
    if source == "tnu":
        articles = soup.find_all("article")
        if not articles:
            raise ValueError("Layout TNU sem artigos publicados reconhecidos")
        result, seen = [], set()
        for article in articles:
            header = article.find("header")
            headings = article.select(".identificacao_processo")
            if header is None or not headings or not re.fullmatch(r"\d+_1", header.get("id", "")):
                raise ValueError("Artigo TNU sem identidade estável e cabeçalho CNJ")
            # Real TNU complaints label both their own and original proceeding.
            # Only the explicit primary segment identifies this document.
            primary = [re.split(r"\bPROCESSO\s+ORIGIN[ÁA]RIO\s*:",
                                h.get_text(" ", strip=True), maxsplit=1,
                                flags=re.IGNORECASE)[0] for h in headings]
            number = _number(" ".join(primary))
            doc_id = header["id"].removesuffix("_1")
            if doc_id in seen:
                raise ValueError("Identificador de artigo TNU repetido")
            seen.add(doc_id)
            # Rodapé de assinatura não integra o texto analítico; bytes ficam na Bronze.
            for footer in article.find_all("footer"):
                footer.decompose()
            text = article.get_text("\n", strip=True)
            if not bpc_text({"ementa": text}):
                continue
            kind = " / ".join(t.get_text(" ", strip=True) for t in article.select(".titulo"))[:100] or "Documento publicado"
            result.append(_document(source, doc_id, canonical, number, text, kind))
        return result
    if source == "trf5_jurisprudencia":
        content = soup.select_one("td.conteudo_body_content")
        if content is None:
            raise ValueError("Layout TRF5 sem conteúdo reconhecido")
        process_cells = [c for c in content.select("td.grid") if c.get_text(" ", strip=True).startswith("Processo:")]
        if len(process_cells) != 1:
            raise ValueError("TRF5 sem campo Processo único")
        original_number = process_cells[0].get_text(" ", strip=True).removeprefix("Processo:").strip()
        # Formato pré-CNJ observado: preservar, jamais completar dígitos ou inferir CNJ.
        number = cnj_number(original_number)
        if number is None:
            number = original_number if re.fullmatch(r"\d{4}\.\d{2}\.\d{2}\.\d{6}-\d", original_number) else _number(original_number)
        text = content.get_text("\n", strip=True)
        # Não confundir página vazia/erro com documento, nem ementa com inteiro teor.
        labels = {t.get_text(" ", strip=True): t for t in content.find_all("b", recursive=False)}
        if "Ementa" not in labels or "Inteiro Teor" not in labels:
            raise ValueError("Seções publicadas TRF5 não reconhecidas")
        parts = []
        for node in labels["Ementa"].next_siblings:
            if getattr(node, "name", None) == "b":
                break
            value = node.get_text(" ", strip=True) if getattr(node, "name", None) else str(node).strip()
            if value:
                parts.append(value)
        ementa = "\n".join(parts) or None
        dates = [c.get_text(" ", strip=True) for c in content.select("td.grid")
                 if c.get_text(" ", strip=True).startswith("Data de Julgamento:")]
        if not bpc_text({"ementa": text}):
            return []
        return [_document(source, identifier, canonical, number, text, "Documento de jurisprudência",
                          ementa=ementa, decision_date=public_date(dates[0]) if len(dates) == 1 else None)]
    # TRF3 identifica o processo no cabeçalho anterior ao RELATÓRIO.
    if source == "trf6_jurisprudencia":
        soup = BeautifulSoup(body.decode("iso-8859-1"), "html.parser")
        content = soup.body
        if (content is None or soup.title is None
                or not soup.title.get_text(" ", strip=True).startswith("Documento:")):
            raise ValueError("Layout TRF6 sem documento publicado reconhecido")
        text = content.get_text("\n", strip=True)
        header = re.split(r"\n(?:PROCESSO ORIGIN\w*|RELAT[\u00d3O]RIO|VOTO|EMENTA|AC[\u00d3O]RD[\u00c3A]O|DESPACHO/DECIS[\u00c3A]O)\s*\n", text, maxsplit=1, flags=re.I)[0]
        header_numbers = {cnj_number(match) for match in re.findall(CNJ, header)}
        header_numbers.discard(None)
        if expected_number is not None:
            expected_number = cnj_number(expected_number)
            if expected_number is None or expected_number not in header_numbers:
                raise ValueError("CNJ da busca TRF6 nao confere com o cabecalho do documento")
            number = expected_number
        else:
            number = _number(header)
        if not bpc_text({"ementa": text}):
            return []
        heading = re.search(r"\n(AC\u00d3RD\u00c3O|DECIS\u00c3O MONOCR\u00c1TICA|DESPACHO/DECIS\u00c3O|S\u00daMULA)\n", text, re.I)
        kind = heading.group(1).title() if heading else "Documento de jurisprudÃªncia"
        return [_document(source, identifier, canonical, number, text, kind)]
    if source in {"trf2_jurisprudencia", "trf4_jurisprudencia"}:
        soup = BeautifulSoup(body.decode("iso-8859-1"), "html.parser")
        if soup.title is None or not soup.title.get_text(" ", strip=True).startswith("Documento:") or soup.body is None:
            raise ValueError(f"Layout {source} sem documento publicado reconhecido")
        text = soup.body.get_text("\n", strip=True)
        header = re.split(r"\n(?:RELAT[ÓO]RIO|VOTO|EMENTA|AC[ÓO]RD[ÃA]O|DECIS[ÃA]O)\s*\n",
                          text, maxsplit=1, flags=re.I)[0]
        header_numbers = {cnj_number(match) for match in re.findall(CNJ, header)}
        header_numbers.discard(None)
        if expected_number is not None:
            expected_number = cnj_number(expected_number)
            if expected_number is None or expected_number not in header_numbers:
                raise ValueError(f"CNJ do card {source} nao confere com o cabecalho do documento")
            number = expected_number
        else:
            number = _number(header)
        if not bpc_text({"ementa": text}):
            return []
        heading = re.search(r"\n(AC[ÓO]RD[ÃA]O|DECIS[ÃA]O MONOCR[ÁA]TICA|VOTO|S[ÚU]MULA)\s*\n", text, re.I)
        kind = heading.group(1).title() if heading else "Documento de jurisprudencia"
        return [_document(source, identifier, canonical, number, text, kind)]
    content = soup.body
    if content is None:
        raise ValueError("Layout TRF3 sem corpo HTML")
    text = content.get_text("\n", strip=True)
    separator = re.search(r"R\s*E\s*L\s*A\s*T\s*[ÓO]\s*R\s*I\s*O", text)
    if separator is None:
        raise ValueError("TRF3 sem seção RELATÓRIO reconhecida")
    number = _number(text[:separator.start()])
    if not bpc_text({"ementa": text}):
        return []
    return [_document(source, identifier, canonical, number, text, "Documento publicado")]
