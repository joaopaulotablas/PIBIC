(async () => {
  const checks = [];
  const check = (ok, label) => { if (!ok) throw new Error(label); checks.push(label); };
  const originalGet = corpusGet;
  try {
    const results = document.getElementById('results'); results.replaceChildren();
    renderDocument({fonte: 'pje_trf1', documento_id: 'fixture', revisao_privacidade: 'pendente', texto: 'PRIVATE_SENTINEL', url_origem: 'https://example.invalid'}, results);
    check(!results.textContent.includes('PRIVATE_SENTINEL') && !results.querySelector('a'), 'privacy-pending corpus hides text and links');
    results.replaceChildren();
    renderDocument({fonte: 'fixture', texto: '<img src=x onerror=alert(1)>', url_origem: 'javascript:alert(1)'}, results);
    check(!results.querySelector('img') && !results.querySelector('a'), 'corpus rejects HTML execution and unsafe links');
    renderDocument({fonte: 'fixture', url_origem: 'not a url'}, results);
    check(results.querySelectorAll('article').length === 2, 'invalid source URL does not abort remaining documents');
    corpusGet = async () => ({schema_disponivel: true, total: 0, itens: []}); await load();
    check(document.getElementById('status').textContent.includes('Nenhum documento') && document.getElementById('next').disabled, 'zero results show honest empty state');
    corpusGet = async () => ({schema_disponivel: false, total: 0, itens: []}); await load();
    check(document.getElementById('status').textContent.includes('tabelas complementares ausentes'), 'missing schema is unavailable instead of empty corpus');
    corpusGet = async () => { throw new Error('HTTP 503'); }; await load();
    check(document.getElementById('status').textContent.includes('indisponível') && results.children.length === 0, 'request failure clears stale documents and reports error');
    let requested = '';
    document.getElementById('source').value = 'pje_trf1'; document.getElementById('query').value = 'fixture-query'; offset = 20;
    corpusGet = async url => { requested = url; return {schema_disponivel: true, total: 41, itens: [{fonte: 'fixture'}]}; }; await load();
    const params = new URL('http://local' + requested).searchParams;
    check(params.get('fonte') === 'pje_trf1' && params.get('texto') === 'fixture-query' && params.get('offset') === '20', 'source search and page offset use API contract');
    check(!document.getElementById('prev').disabled && !document.getElementById('next').disabled, 'pagination availability follows result count');
    let resolveOld;
    corpusGet = () => new Promise(resolve => { resolveOld = resolve; });
    const old = load(); corpusRequest++; results.textContent = 'NEW_SELECTION';
    resolveOld({schema_disponivel: true, total: 0, itens: []}); await old;
    check(results.textContent === 'NEW_SELECTION', 'stale corpus response cannot overwrite a new search');
    return {passed: checks.length, checks};
  } finally { corpusGet = originalGet; offset = 0; document.getElementById('source').value = ''; document.getElementById('query').value = ''; }
})()
