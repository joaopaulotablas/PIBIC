let offset = 0, total = 0, corpusRequest = 0;
const el = id => document.getElementById(id);
function add(parent, tag, text) { const node = document.createElement(tag); if (text != null) node.textContent = String(text); parent.append(node); return node; }
async function corpusGet(url) { const response = await fetch(url); if (!response.ok) throw new Error('Falha HTTP ' + response.status); return response.json(); }
function renderDocument(item, parent) {
  const article = add(parent, 'article');
  const heading = add(article, 'div'); heading.className = 'document-row';
  const identity = add(heading, 'div');
  add(identity, 'h2', `${item.tipo_documento || 'Documento'} · ${item.tribunal || item.fonte || 'Fonte não informada'}`);
  add(identity, 'small', `${item.fonte || 'Fonte não informada'} · ID ${item.documento_id || 'Não informado'}`);
  const published = add(heading, 'div'); add(published, 'small', 'Publicação'); add(published, 'span', item.data_publicacao || 'Não informada');
  const status = add(heading, 'span', item.revisao_privacidade === 'pendente' ? 'Privacidade pendente' : 'Revisão humana necessária'); status.className = 'badge';
  add(article, 'p', `Referência: ${item.numero_origem || 'Não informada'} · CNJ explícito: ${(item.numeros_cnj || []).join(', ') || 'Não informado; sem vínculo automático'}`);
  if (item.revisao_privacidade === 'pendente') { add(article, 'p', 'Conteúdo e links retidos por revisão de privacidade. Documento armazenado localmente; a retenção não significa ausência de texto.'); return; }
  const explanations = {pendente: 'Arquivo original disponível, com texto pendente de conversão ou OCR.', texto_simples: 'Texto simples publicado pela fonte, sem OCR. Revisão humana necessária.', doc_legacy_preliminar: 'Conversão local preliminar de DOC antigo, sem garantia de integridade.'};
  if (explanations[item.extracao_texto]) add(article, 'p', explanations[item.extracao_texto]);
  for (const [label, text] of [['Ementa', item.ementa], ['Decisão publicada', item.decisao], ['Texto publicado', item.texto]]) {
    if (text) { const details = add(article, 'details'); details.className = 'corpus-body'; add(details, 'summary', label); add(details, 'pre', text); }
  }
  if (!item.ementa && !item.decisao && !item.texto) add(article, 'p', 'Texto não disponibilizado neste registro.');
  try { const url = new URL(item.url_origem); if (url.protocol === 'https:') { const link = add(article, 'a', 'Abrir fonte oficial ↗'); link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer'; } } catch {}
}
async function load() {
  const request = ++corpusRequest;
  el('status').textContent = 'Consultando corpus…'; el('results').replaceChildren(); el('results').setAttribute('aria-busy', 'true');
  el('prev').disabled = true; el('next').disabled = true; el('corpus-page').textContent = '';
  try {
    const params = new URLSearchParams({limit: 20, offset});
    if (el('source').value) params.set('fonte', el('source').value);
    if (el('query').value.trim()) params.set('texto', el('query').value.trim());
    const data = await corpusGet('/admin/api/documentos?' + params); if (request !== corpusRequest) return;
    total = data.total;
    el('status').textContent = !data.schema_disponivel ? 'Corpus indisponível: tabelas complementares ausentes nesta base.' : !total ? 'Nenhum documento encontrado com estes filtros.' : `${new Intl.NumberFormat('pt-BR').format(total)} versões encontradas. Origem preservada; revisão humana pendente.`;
    (data.itens || []).forEach(item => renderDocument(item, el('results')));
    el('corpus-page').textContent = total ? `${offset + 1}–${offset + data.itens.length} de ${total}` : '0 resultados';
    el('prev').disabled = offset === 0; el('next').disabled = offset + data.itens.length >= total;
  } catch (error) { if (request === corpusRequest) el('status').textContent = `Corpus indisponível: ${error.message}. Pesquise novamente para tentar outra vez.`; }
  finally { if (request === corpusRequest) el('results').setAttribute('aria-busy', 'false'); }
}
el('filter').addEventListener('submit', event => { event.preventDefault(); offset = 0; load(); });
el('prev').onclick = () => { offset = Math.max(0, offset - 20); load(); };
el('next').onclick = () => { offset += 20; load(); };
async function loadAggregate(target, url, titles, values) {
  try {
    const data = await corpusGet(url); el(target).replaceChildren();
    if (!data.itens?.length) { const empty = add(el(target), 'p', 'Nenhum agregado coletado nesta base.'); empty.className = 'empty'; return; }
    const table = add(el(target), 'table'), head = add(table, 'thead'), heading = add(head, 'tr'), body = add(table, 'tbody');
    titles.forEach(title => { const th = add(heading, 'th', title); th.scope = 'col'; });
    data.itens.forEach(item => { const row = add(body, 'tr'); values(item).forEach(value => add(row, 'td', value ?? 'Não informado')); });
  } catch (error) { el(target).replaceChildren(); const message = add(el(target), 'p', `Agregado indisponível: ${error.message}`); message.className = 'empty error'; }
}
function loadInss() { return loadAggregate('inss', '/admin/api/indeferimentos-inss?uf=DF', ['Competência', 'Espécie', 'Motivo publicado', 'Indeferimentos'], item => [item.competencia, item.especie === 87 ? 'BPC · deficiência' : 'BPC · idoso', item.motivo, item.quantidade]); }
function loadGrants() { return loadAggregate('grants', '/admin/api/concessoes-inss?uf=DF', ['Competência', 'Espécie', 'Código despacho', 'Descrição publicada', 'Concessões'], item => [item.competencia, item.especie === 87 ? 'BPC · deficiência' : 'BPC · idoso', item.codigo_despacho, item.despacho, item.quantidade]); }
load(); loadInss(); loadGrants();
