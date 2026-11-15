// Execute in the local Orca browser after loading /admin/processos.
// Synthetic fixtures stay in the DOM only. No writes, model calls or personal data.
(async () => {
  const checks = [];
  const check = (value, name) => { if (!value) throw new Error(name); checks.push(name); };
  const originalGet = get;
  const originalRequest = state.detailRequest;
  const fixture = () => ({numero_processo: '0000000-00.2024.4.01.0000', registros_datajud: [], comunicacoes_pje: [], documentos_publicos: [], extracoes_ia: [], documento_chunks: [], consulta_comunica: null});
  try {
    renderDetail(fixture());
    check(document.getElementById('review').textContent.includes('comprovação indisponível'), 'empty case never claims human review');
    check(document.getElementById('documents').textContent.includes('Nenhum documento'), 'empty documents are explicit');
    const populated = fixture();
    populated.registros_datajud = [{id: 7, tribunal: 'TRF1', grau: 'G1', classe: {}, orgao_julgador: {}, assuntos: [], movimentacoes: [{data_hora: '2024-01-01T00:00:00', nome: 'Anterior'}, {data_hora: '2025-01-01T00:00:00', nome: 'Recente'}]}];
    populated.comunicacoes_pje = [{id: 9, texto: '<img src=x onerror=alert(1)>', link: 'javascript:alert(1)'}];
    populated.documentos_publicos = [{id: 8, fonte: 'pje_trf1', revisao_privacidade: 'pendente', texto: 'DO_NOT_RENDER_PRIVATE', hash_conteudo: 'synthetic'}];
    populated.extracoes_ia = [{tipo_extracao: 'triagem_bpc', status_validacao: 'validado', resultado: {resumo_caso: '<script>alert(1)</script>', escopo_pedido: 'indeterminado', evidencias: [{registro_id: 7, campo: 'classe', referencia: 'Registro de teste', sustenta: 'escopo_pedido'}], lacunas: ['Petição ausente']}}];
    renderDetail(populated);
    check(!document.querySelector('#detail img, #detail script'), 'untrusted source HTML is rendered as text');
    check(!document.querySelector('#detail a[href^=javascript]'), 'unsafe original link is rejected');
    check(!document.getElementById('documents').textContent.includes('DO_NOT_RENDER_PRIVATE'), 'privacy-pending document text is hidden');
    check(document.querySelector('#timeline .event').textContent.includes('Recente'), 'timeline sorts by date descending');
    check(document.querySelector('#analysis a').textContent.includes('Conferir fonte'), 'metadata evidence resolves to source in same case');
    check(document.getElementById('analysis').textContent.includes('Petição ausente'), 'gaps are readable without opening JSON');
    check(document.getElementById('review').textContent.includes('comprovação indisponível'), 'validated extraction does not claim human review');
    const root = document.getElementById('document-analysis');
    const documentary = {revisao_humana: 'pendente', revisao_privacidade: 'pendente', texto_retido: true, extracoes: [{resultado: {resumo_caso: 'DO_NOT_RENDER_PRIVATE', evidencias: [{documento_id: 8, campo: 'texto', inicio: 1, fim: 2, trecho: 'DO_NOT_RENDER_PRIVATE'}]}}], documentos: [], lacunas: []};
    renderDocumentAnalysis(root, documentary, populated.numero_processo, state.detailRequest);
    check(!root.textContent.includes('DO_NOT_RENDER_PRIVATE'), 'documentary privacy gate also hides accidentally supplied narrative');
    check(root.textContent.includes('Solicitar leitura local'), 'local text requires explicit action');
    delete documentary.texto_retido;
    renderDocumentAnalysis(root, documentary, populated.numero_processo, state.detailRequest);
    check(!root.textContent.includes('DO_NOT_RENDER_PRIVATE'), 'missing privacy flag defaults to retained');
    documentary.texto_retido = false;
    documentary.documentos = [{id: 8, texto: '😀áX'}];
    documentary.extracoes[0].resultado = {resumo_caso: 'Resumo sintético de teste', desfecho: {resultado: 'indeterminado', natureza: 'provisoria', transito_julgado: 'nao'}, evidencias: [{documento_id: 8, inicio: 1, fim: 2, trecho: 'á'}]};
    renderDocumentAnalysis(root, documentary, populated.numero_processo, state.detailRequest);
    check(root.textContent.includes('Trecho coincide'), 'Unicode codepoint offsets match Python instead of JS UTF-16');
    documentary.extracoes[0].resultado.evidencias[0].fim = 100;
    documentary.extracoes[0].resultado.evidencias[0].trecho = 'áX';
    renderDocumentAnalysis(root, documentary, populated.numero_processo, state.detailRequest);
    check(root.textContent.includes('não coincide'), 'out-of-range evidence interval is rejected');
    documentary.extracoes[0].resultado.evidencias[0].fim = 2;
    documentary.extracoes[0].resultado.evidencias[0].trecho = 'WRONG';
    renderDocumentAnalysis(root, documentary, populated.numero_processo, state.detailRequest);
    check(root.textContent.includes('não coincide'), 'mismatched quotation is flagged');
    get = async () => { throw new Error('HTTP 503'); };
    await loadDocumentAnalysis(populated.numero_processo, state.detailRequest);
    check(root.textContent.includes('indisponível') && root.querySelector('button'), 'endpoint failure offers retry without claiming zero data');
    let resolveOld;
    get = () => new Promise(resolve => { resolveOld = resolve; });
    const pending = loadDetail('0000000-00.2024.4.01.0001');
    state.detailRequest += 1;
    document.getElementById('detail').textContent = 'NEW_SELECTION';
    resolveOld(fixture()); await pending;
    check(document.getElementById('detail').textContent === 'NEW_SELECTION', 'stale detail request cannot overwrite new selection');
    return {passed: checks.length, checks};
  } finally {
    get = originalGet;
    state.detailRequest = originalRequest;
    renderDetail(fixture());
  }
})()
