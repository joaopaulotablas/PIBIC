let selectedTask = null;
    let pollHandle = null;
    const $ = (id) => document.getElementById(id);
    const number = (value) => new Intl.NumberFormat('pt-BR').format(value || 0);
    const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, character => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[character]));

    async function request(url, options = {}) {
      const response = await fetch(url, {headers: {'Content-Type': 'application/json'}, ...options});
      if (!response.ok) {
        let message = `Erro HTTP ${response.status}`;
        try { const body = await response.json(); message = body.detail || message; } catch (_) {}
        throw new Error(message);
      }
      return response.json();
    }

    function toast(message, error = false) {
      const node = $('toast');
      node.textContent = message;
      node.className = `toast show${error ? ' error' : ''}`;
      setTimeout(() => node.className = 'toast', 3800);
    }

    function markStep(id, done) { $(id).classList.toggle('done', Boolean(done)); }

    async function refreshSummary() {
      try {
        await request('/health');
        $('health-dot').className = 'dot online';
        $('health-text').textContent = 'Banco e API online';
        markStep('step-infra', true);
        const data = await request('/resumo');
        const t = data.totais;
        $('m-processos').textContent = number(t.processos);
        $('m-registros').textContent = number(t.registros_datajud);
        $('m-movimentos').textContent = number(t.movimentos);
        $('m-comunicacoes').textContent = number(t.comunicacoes_pje);
        $('m-tpu').textContent = number(t.referencias_tpu);
        markStep('step-tpu', t.referencias_tpu > 0);
        markStep('step-datajud', t.registros_datajud > 0);
        const queried = Object.values(data.cobertura_pje || {}).reduce((a, b) => a + b, 0);
        markStep('step-pje', queried > 0);
        markStep('step-analysis', t.registros_datajud > 0);
        const tbody = $('tribunal-table');
        tbody.innerHTML = data.tribunais.length ? data.tribunais.map(row => `
          <tr><td>${escapeHtml(row.tribunal || 'Não informado')}</td><td>${number(row.processos)}</td><td>${number(row.registros_datajud)}</td><td>${number(row.movimentos)}</td><td>${number(row.comunicacoes_pje)}</td></tr>
        `).join('') : '<tr><td colspan="5" class="empty">Nenhum dado coletado.</td></tr>';
        const related = await request('/analises/assuntos-relacionados?limit=15');
        $('related-table').innerHTML = related.length ? related.map(row => `
          <tr><td>${escapeHtml(row.codigo)}</td><td>${escapeHtml(row.nome || 'Não informado')}</td><td>${number(row.registros)}</td></tr>
        `).join('') : '<tr><td colspan="3" class="empty">Nenhum assunto adicional encontrado.</td></tr>';
      } catch (error) {
        $('health-dot').className = 'dot offline';
        $('health-text').textContent = `Serviço indisponível: ${error.message}`;
      }
    }

    function setBusy(busy) { document.querySelectorAll('.operation').forEach(button => button.disabled = busy); }

    async function startTask(endpoint, payload) {
      setBusy(true);
      try {
        const task = await request(endpoint, {method: 'POST', body: payload === undefined ? undefined : JSON.stringify(payload)});
        selectedTask = task.id;
        toast('Tarefa iniciada. Acompanhe os passos no log.');
        await refreshTask();
        await refreshHistory();
      } catch (error) { toast(error.message, true); await refreshHistory(); }
    }

    async function refreshTask() {
      if (!selectedTask) return;
      try {
        const task = await request(`/tarefas/${selectedTask}`);
        $('task-status').textContent = task.status.replace('_', ' ');
        $('task-status').className = `badge ${task.status}`;
        $('task-meta').textContent = `${task.tipo} · criada em ${new Date(task.criado_em).toLocaleString('pt-BR')}`;
        const log = $('task-log');
        const atBottom = log.scrollTop + log.clientHeight >= log.scrollHeight - 35;
        log.textContent = task.log || 'Aguardando mensagens…';
        if (atBottom) log.scrollTop = log.scrollHeight;
        const running = ['na_fila', 'executando'].includes(task.status);
        setBusy(running);
        document.querySelectorAll('.step').forEach(step => step.classList.remove('active'));
        if (running) {
          const map = {tpu: 'step-tpu', datajud: 'step-datajud', comunica_pje: 'step-pje', inss_catalogo: 'step-analysis'};
          if (map[task.tipo]) $(map[task.tipo]).classList.add('active');
        } else {
          selectedTask = null;
          await refreshSummary();
          await refreshHistory();
        }
      } catch (error) { toast(error.message, true); }
    }

    async function refreshHistory() {
      try {
        const tasks = await request('/tarefas?limit=12');
        const history = $('history');
        history.innerHTML = tasks.length ? tasks.map(task => `
          <button class="job" type="button" data-id="${escapeHtml(task.id)}">
            <span><strong>${escapeHtml(task.tipo)}</strong><small>${new Date(task.criado_em).toLocaleString('pt-BR')}</small></span>
            <span class="badge ${escapeHtml(task.status)}">${escapeHtml(task.status.replace('_', ' '))}</span>
          </button>`).join('') : '<div class="empty">Nenhuma tarefa registrada.</div>';
        history.querySelectorAll('.job').forEach(button => button.addEventListener('click', async () => {
          selectedTask = button.dataset.id;
          await refreshTask();
        }));
        const active = tasks.find(task => ['na_fila', 'executando'].includes(task.status));
        if (active && !selectedTask) { selectedTask = active.id; await refreshTask(); }
        setBusy(Boolean(active));
      } catch (error) { toast(error.message, true); }
    }

    $('datajud-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const tribunais = [...document.querySelectorAll('#tribunais input:checked')].map(input => input.value);
      const assuntos = [...document.querySelectorAll('#assuntos input:checked')].map(input => Number(input.value));
      if (!tribunais.length) return toast('Selecione ao menos um tribunal.', true);
      if (!assuntos.length) return toast('Selecione ao menos um assunto.', true);
      const rawLimit = $('max-records').value.trim();
      if (!rawLimit && !confirm('Sem limite, a coleta pode demorar muitas horas. Deseja continuar?')) return;
      await startTask('/tarefas/datajud', {
        tribunais,
        assuntos,
        page_size: Number($('page-size').value),
        max_records: rawLimit ? Number(rawLimit) : null,
        restart: $('restart').checked,
        source_mode: $('source-mode').value,
        municipio_codigos: $('only-df').checked ? [743] : [],
        graus: $('first-instance').checked ? ['G1', 'JE'] : [],
        include_state_courts: $('include-state-courts').checked
      });
    });
    $('pje-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      await startTask('/tarefas/comunica', {limit: Number($('pje-limit').value), retry_errors: $('retry-errors').checked});
    });
    $('tpu-button').addEventListener('click', () => startTask('/tarefas/importar-tpu'));
    $('inss-button').addEventListener('click', () => startTask('/tarefas/catalogar-inss'));
    $('refresh').addEventListener('click', async () => { await refreshSummary(); await refreshHistory(); toast('Dados atualizados.'); });

    async function boot() {
      await refreshSummary();
      await refreshHistory();
      pollHandle = setInterval(async () => { await refreshTask(); }, 1200);
      setInterval(refreshSummary, 10000);
    }
    boot();
