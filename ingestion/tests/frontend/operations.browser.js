// Browser-only synthetic regression. All operation submissions are intercepted.
(async () => {
  const checks = [], calls = [];
  const check = (ok, label) => { if (!ok) throw new Error(label); checks.push(label); };
  const originalStart = startTask, originalRequest = request, originalSelected = selectedTask;
  const values = Array.from(document.querySelectorAll('input,select')).map(node => [node, node.value, node.checked]);
  try {
    startTask = async (endpoint, payload) => { calls.push({endpoint, payload}); };
    document.getElementById('only-df').checked = true;
    document.getElementById('datajud-form').dispatchEvent(new Event('submit', {cancelable: true, bubbles: true}));
    await Promise.resolve();
    check(calls[0].endpoint === '/tarefas/datajud', 'DataJud submit keeps endpoint');
    check(calls[0].payload.tribunais.join() === 'TRF1' && calls[0].payload.assuntos.length === 3, 'tribunal and subject selections preserved');
    check(calls[0].payload.municipio_codigos[0] === 743 && calls[0].payload.graus.join() === 'G1,JE', 'territory and grade payload preserved');
    check(calls[0].payload.page_size === 50 && calls[0].payload.max_records === 100 && !calls[0].payload.restart, 'limits and continuation preserved');
    document.getElementById('pje-limit').value = '25'; document.getElementById('retry-errors').checked = true;
    document.getElementById('pje-form').dispatchEvent(new Event('submit', {cancelable: true, bubbles: true})); await Promise.resolve();
    check(calls[1].endpoint === '/tarefas/comunica' && calls[1].payload.limit === 25 && calls[1].payload.retry_errors, 'communication submit preserves limit and retry');
    document.getElementById('tpu-button').click(); document.getElementById('inss-button').click();
    check(calls[2].endpoint === '/tarefas/importar-tpu' && calls[3].endpoint === '/tarefas/catalogar-inss', 'TPU and INSS operation endpoints preserved');
    document.querySelectorAll('#tribunais input').forEach(node => { node.checked = false; });
    document.getElementById('datajud-form').dispatchEvent(new Event('submit', {cancelable: true, bubbles: true})); await Promise.resolve();
    check(calls.length === 4 && document.getElementById('toast').classList.contains('error'), 'empty tribunal blocks operation');
    check(escapeHtml('<img onerror=x>') === '&lt;img onerror=x&gt;', 'source data is escaped in summary tables');
    selectedTask = 'synthetic-task';
    request = async () => ({id: 'synthetic-task', tipo: 'datajud', status: 'executando', criado_em: '2024-01-01T00:00:00Z', log: 'SYNTHETIC_LOG'});
    await refreshTask();
    check(document.getElementById('task-log').textContent === 'SYNTHETIC_LOG' && document.getElementById('task-status').textContent === 'executando', 'monitor shows exact log and status');
    check(Array.from(document.querySelectorAll('.operation')).every(button => button.disabled), 'active task disables operation buttons');
    selectedTask = null; request = async () => [];
    await refreshHistory();
    check(document.getElementById('history').textContent.includes('Nenhuma tarefa') && Array.from(document.querySelectorAll('.operation')).every(button => !button.disabled), 'empty history restores operation availability');
    request = async () => { throw new Error('SYNTHETIC_FAILURE'); };
    await refreshSummary();
    check(document.getElementById('health-text').textContent.includes('indisponível'), 'service error is explicit');
    return {passed: checks.length, checks, realOperationsStarted: 0};
  } finally {
    startTask = originalStart; request = originalRequest; selectedTask = originalSelected;
    values.forEach(([node, value, checked]) => { node.value = value; node.checked = checked; });
    setBusy(false);
  }
})()
