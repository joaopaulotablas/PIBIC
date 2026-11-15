const $ = id => document.getElementById(id);
    const fmt = value => new Intl.NumberFormat('pt-BR').format(value ?? 0);
    const when = value => { if (!value) return 'Não informado'; const date = new Date(/^\d{4}-\d\d-\d\dT/.test(value) && !/(Z|[+-]\d\d:\d\d)$/.test(value) ? value + 'Z' : value); return Number.isNaN(date.getTime()) ? 'Data não interpretável' : date.toLocaleString('pt-BR', {timeZone: 'UTC'}) + ' UTC'; };
    const state = {offset: 0, limit: 25, total: 0, selected: null, listRequest: 0, detailRequest: 0};
    const el = (tag, text, className) => { const node = document.createElement(tag); if (text != null) node.textContent = String(text); if (className) node.className = className; return node; };
    const add = (parent, tag, text, className) => { const node = el(tag, text, className); parent.append(node); return node; };
    async function get(url) { const response = await fetch(url); if (!response.ok) { let reason = `HTTP ${response.status}`; try { reason = (await response.json()).detail || reason; } catch {} throw new Error(reason); } return response.json(); }
    function fact(parent, label, value) { const box = add(parent, 'div'); add(box, 'small', label); add(box, 'span', value ?? 'Não informado'); }
    function empty(parent, text) { add(parent, 'p', text, 'muted'); }
    function raw(parent, payload) { const details = add(parent, 'details'); add(details, 'summary', 'Ver payload original'); add(details, 'pre', JSON.stringify(payload ?? {}, null, 2)); }
    function section(parent, id, title) { const node = add(parent, 'section', null, 'section'); node.id = id; add(node, 'h3', title); return node; }
    function sourceLink(parent, value, label) { if (!value) return; try { const url = new URL(value); if (!['https:', 'http:'].includes(url.protocol)) return; const link = add(parent, 'a', label); link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer'; } catch {} }
    function readable(value) { if (value == null) return 'Não informado'; return typeof value === 'object' ? JSON.stringify(value) : String(value).replaceAll('_', ' '); }
    async function loadStats() {
      try {
        const data = await get('/resumo'); const t = data.totais; const stats = $('stats'); stats.replaceChildren();
        [['Processos únicos', t.processos], ['Registros DataJud', t.registros_datajud], ['Movimentações', t.movimentos], ['Publicações', t.comunicacoes_pje], ['Extrações de IA', t.extracoes_ia]].forEach(([label, value]) => {
          const card = add(stats, 'div', null, 'stat'); add(card, 'small', label); add(card, 'strong', fmt(value));
        });
      } catch (error) { $('stats').textContent = `Não foi possível consultar o resumo: ${error.message}`; }
    }
    async function loadList() {
      const request = ++state.listRequest;
      const params = new URLSearchParams({limit: state.limit, offset: state.offset});
      const number = $('number-filter').value.trim(), tribunal = $('tribunal-filter').value, communication = $('communication-filter').value;
      const municipio = $('municipio-filter').value, grau = $('grau-filter').value;
      if (number) params.set('numero', number);
      if (tribunal) params.set('tribunal', tribunal);
      if (municipio) params.set('municipio_codigo', municipio);
      if (grau) params.set('grau', grau);
      if (communication) params.set('com_comunicacao', communication);
      $('list-status').textContent = 'Buscando processos…'; $('list-status').className = 'message';
      $('process-list').replaceChildren(); $('process-list').setAttribute('aria-busy', 'true');
      $('previous').disabled = true; $('next').disabled = true; $('page-label').textContent = '';
      try {
        const data = await get(`/admin/api/processos?${params}`); if (request !== state.listRequest) return; state.total = data.total;
        const list = $('process-list'); list.replaceChildren();
        data.items.forEach(item => {
          const button = add(list, 'button', null, 'process-row' + (item.numero_processo === state.selected ? ' selected' : ''));
          button.type = 'button'; add(button, 'strong', item.numero_processo);
          button.setAttribute('aria-pressed', String(item.numero_processo === state.selected));
          button.setAttribute('aria-controls', 'dossier');
          add(button, 'small', `${item.tribunais || 'Tribunal não informado'} · ${fmt(item.registros_datajud)} registro(s) DataJud · ${fmt(item.comunicacoes_pje)} publicação(ões) · ${fmt(item.extracoes_ia)} extração(ões)`);
          button.addEventListener('click', () => loadDetail(item.numero_processo, true));
        });
        $('list-status').textContent = data.total ? `${fmt(data.total)} processo(s) encontrados` : 'Nenhum processo encontrado com esses filtros.';
        $('page-label').textContent = data.total ? `${fmt(state.offset + 1)}–${fmt(state.offset + data.items.length)} de ${fmt(data.total)}` : '0 de 0';
        $('previous').disabled = state.offset === 0;
        $('next').disabled = state.offset + data.items.length >= data.total;
      } catch (error) { if (request !== state.listRequest) return; $('list-status').textContent = `Não foi possível listar processos: ${error.message}. Use Buscar para tentar novamente.`; $('list-status').className = 'message error'; }
      finally { if (request === state.listRequest) $('process-list').setAttribute('aria-busy', 'false'); }
    }
    async function loadDetail(number, focus = false) {
      const request = ++state.detailRequest;
      state.selected = number; $('detail').replaceChildren(); $('detail-status').textContent = 'Carregando processo…'; $('detail-status').className = 'message'; $('detail').setAttribute('aria-busy', 'true');
      document.querySelectorAll('.process-row').forEach(node => { const selected = node.querySelector('strong')?.textContent === number; node.classList.toggle('selected', selected); node.setAttribute('aria-pressed', String(selected)); });
      try { const data = await get(`/admin/api/processos/${encodeURIComponent(number)}`); if (request !== state.detailRequest) return; renderDetail(data); loadDocumentAnalysis(number, request); history.replaceState(null, '', `#${encodeURIComponent(number)}`); $('detail-status').textContent = 'Processo carregado.'; if (focus) { $('dossier').focus({preventScroll: true}); if (matchMedia('(max-width: 900px)').matches) $('dossier').scrollIntoView(); } }
      catch (error) { if (request !== state.detailRequest) return; $('detail-status').textContent = `Não foi possível abrir o processo: ${error.message}`; $('detail-status').className = 'message error'; const retry = add($('detail'), 'button', 'Tentar abrir novamente', 'secondary'); retry.type = 'button'; retry.addEventListener('click', () => loadDetail(number, focus)); }
      finally { if (request === state.detailRequest) $('detail').setAttribute('aria-busy', 'false'); }
    }
    function renderDetail(data) {
      const root = $('detail'); root.className = ''; root.replaceChildren();
      const head = add(root, 'div', null, 'detail-head'); add(head, 'h2', data.numero_processo); add(head, 'span', `${data.registros_datajud.length} registro(s) DataJud`, 'pill');
      const navigation = add(root, 'nav', null, 'section-nav'); navigation.setAttribute('aria-label', 'Seções do processo');
      [['cover', 'Capa DataJud'], ['timeline', 'Linha do tempo'], ['documents', 'Documentos'], ['analysis', 'Triagem IA'], ['document-analysis', 'Análise documental'], ['review', 'Revisão']].forEach(([id, title]) => { const link = add(navigation, 'a', title); link.href = '#' + id; link.addEventListener('click', event => { event.preventDefault(); const target = $(id); target.tabIndex = -1; target.focus(); target.scrollIntoView(); }); });
      const notice = add(root, 'div', null, 'notice');
      notice.textContent = data.extracoes_ia.length ? 'Há extrações registradas abaixo. Confira o texto de origem e o status de validação antes de interpretar o resultado.' : 'Não há resultado jurídico extraído neste processo. Uma movimentação “Sentença” sozinha não indica concessão ou negativa.';

      const recordSection = section(root, 'cover', 'Capa DataJud');
      add(recordSection, 'p', 'Órgão julgador e assuntos descrevem o registro de origem. Não confirmam residência, elegibilidade ou concessão.', 'muted');
      if (!data.registros_datajud.length) empty(recordSection, 'Nenhum registro DataJud associado.');
      data.registros_datajud.forEach(record => {
        const card = add(recordSection, 'article', null, 'entry'); card.id = `record-${record.id}`; add(card, 'h4', `${record.tribunal || 'Tribunal desconhecido'} · ${record.grau || 'Grau não informado'} · registro ${record.id}`);
        const facts = add(card, 'div', null, 'facts');
        fact(facts, 'Classe', `${record.classe.codigo ?? '—'} · ${record.classe.nome || 'Não informada'}`);
        fact(facts, 'Órgão julgador', record.orgao_julgador.nome || 'Não informado');
        fact(facts, 'Ajuizamento', when(record.data_ajuizamento));
        fact(facts, 'Última atualização no DataJud', when(record.data_ultima_atualizacao));
        fact(facts, 'Sigilo', record.nivel_sigilo === 0 ? 'Público' : record.nivel_sigilo ?? 'Não informado');
        fact(facts, 'Coletado em', when(record.coletado_em));
        add(card, 'p', `Assuntos: ${record.assuntos.map(item => `${item.codigo} · ${item.nome || 'sem nome'}`).join('; ') || 'não informados'}`);
        raw(card, record.payload_original);
      });

      const timeline = section(root, 'timeline', 'Linha do tempo');
      add(timeline, 'p', 'Movimentações DataJud em ordem de data, da mais recente à mais antiga. Movimentos de registros distintos são preservados; não são decisões interpretadas.', 'muted');
      const movements = data.registros_datajud.flatMap(record => record.movimentacoes.map(item => ({...item, record})));
      movements.sort((a, b) => (Date.parse(b.data_hora) || 0) - (Date.parse(a.data_hora) || 0));
      if (!movements.length) empty(timeline, 'Nenhuma movimentação registrada.');
      const events = add(timeline, 'div', null, 'events'); events.tabIndex = 0; events.setAttribute('role', 'region'); events.setAttribute('aria-label', 'Movimentações do DataJud, área de rolagem');
      movements.forEach(item => { const row = add(events, 'article', null, 'event'); add(row, 'small', when(item.data_hora)); add(row, 'div', `${item.codigo ?? 'Não informado'} · ${item.nome || 'Sem nome'}`); add(row, 'small', `${item.record.tribunal || 'Tribunal não informado'} / ${item.record.grau || 'Grau não informado'} · registro ${item.record.id}`); });

      const commSection = section(root, 'documents', 'Documentos e publicações');
      add(commSection, 'h4', 'Comunica PJe: atos publicados');
      const consult = data.consulta_comunica;
      add(commSection, 'p', consult ? `Consulta: ${consult.status} · ${when(consult.consultado_em)} · ${fmt(consult.quantidade)} item(ns)${consult.erro ? ` · erro: ${consult.erro}` : ''}` : 'Ainda não há consulta ao Comunica PJe registrada.');
      if (!data.comunicacoes_pje.length) empty(commSection, 'Nenhuma publicação vinculada a este número no banco.');
      data.comunicacoes_pje.forEach(item => {
        const card = add(commSection, 'article', null, 'entry'); card.id = `communication-${item.id}`; add(card, 'h4', `${item.tipo_documento || item.tipo_comunicacao || 'Ato publicado'} · ${item.data_disponibilizacao || 'Data não informada'}`);
        add(card, 'p', item.orgao_nome || 'Órgão não informado', 'muted');
        const body = add(card, 'details', null, 'document-body'); add(body, 'summary', `Ler texto publicado · comunicação ${item.id}`);
        if (item.texto) add(body, 'div', item.texto, 'text'); else empty(body, 'O texto da publicação não foi recebido.');
        if (item.link) { try { const url = new URL(item.link); if (['https:', 'http:'].includes(url.protocol)) { const link = add(card, 'a', 'Abrir publicação original ↗'); link.href = url.href; link.target = '_blank'; link.rel = 'noopener noreferrer'; } } catch {} }
        raw(card, item.payload_original);
      });

      add(commSection, 'h4', 'Documentos públicos vinculados por CNJ');
      if (!data.documentos_publicos?.length) empty(commSection, 'Nenhum documento público vinculado no banco. Isso não significa ausência de documentos nos autos.');
      (data.documentos_publicos || []).forEach(item => {
        const card = add(commSection, 'article', null, 'entry'); card.id = `document-${item.id}`;
        add(card, 'h4', `${item.tipo_documento || 'Documento público'} · ${item.fonte || 'Fonte não informada'}`);
        add(card, 'p', item.fonte === 'pje_trf1' ? 'Documento próprio publicado no PJe, vinculado por CNJ. Não equivale aos autos completos nem confirma concessão inicial.' : 'Corpus complementar: vínculo explícito por CNJ, sem inclusão automática na amostra ou confirmação do resultado.', 'muted');
        const metadata = add(card, 'div', null, 'facts'); fact(metadata, 'ID da fonte', item.documento_id); fact(metadata, 'Coletado em', when(item.coletado_em)); fact(metadata, 'Data de publicação', item.data_publicacao); fact(metadata, 'Data da decisão', item.data_decisao);
        if (item.revisao_privacidade === 'pendente') add(card, 'p', 'Texto e links indisponíveis: revisão de privacidade pendente na API.', 'notice');
        else { const body = add(card, 'details', null, 'document-body'); add(body, 'summary', 'Ler conteúdo disponível'); if (item.ementa) { add(body, 'h4', 'Ementa'); add(body, 'div', item.ementa, 'text'); } if (item.decisao) { add(body, 'h4', 'Decisão publicada'); add(body, 'div', item.decisao, 'text'); } if (item.texto) add(body, 'div', item.texto, 'text'); if (!item.ementa && !item.decisao && !item.texto) empty(body, 'Texto não disponibilizado pelo endpoint.'); sourceLink(card, item.recurso_url || item.url_origem, 'Abrir documento na fonte oficial ↗'); }
        const provenance = add(card, 'details'); add(provenance, 'summary', 'Identificação e proveniência'); add(provenance, 'p', `ID local: ${item.id} · SHA-256: ${item.hash_conteudo || 'Não informado'}`);
      });

      const extractionSection = section(root, 'analysis', 'Explicação e extrações de IA');
      add(extractionSection, 'p', 'Resultados automáticos para orientar a leitura. Modelo, versão e evidências devem ser conferidos; resumo e confiança não substituem revisão humana.', 'muted');
      const historicalExtractions = data.extracoes_ia.filter(item => item.tipo_extracao !== 'documento_bpc_texto');
      if (!historicalExtractions.length) empty(extractionSection, 'Nenhuma triagem de metadados ou análise de comunicação registrada.');
      historicalExtractions.forEach(item => {
        const card = add(extractionSection, 'article', null, 'entry'); add(card, 'h4', readable(item.tipo_extracao));
        add(card, 'p', `Status registrado na extração: ${item.status_validacao || 'Não informado'}`, 'pill');
        add(card, 'p', `Modelo ${item.modelo} · prompt ${item.versao_prompt} · confiança ${item.confianca ?? 'não informada'} · ${when(item.criado_em)}`, 'muted');
        const summary = item.resultado?.resumo_caso || item.resultado?.observacao_curta;
        if (summary) { add(card, 'h4', 'Resumo do caso'); add(card, 'div', summary, 'text'); }
        else empty(card, 'Resumo não registrado nesta versão da extração.');
        const fields = add(card, 'div', null, 'facts');
        [['escopo_pedido', 'Escopo provável do pedido'], ['aderencia_geografica', 'Aderência geográfica'], ['desfecho', 'Desfecho sugerido'], ['nivel_evidencia', 'Nível de evidência'], ['motivo_judicializacao', 'Motivo da judicialização'], ['motivo_administrativo_negativa', 'Motivo administrativo da negativa'], ['resultado_judicial', 'Resultado judicial sugerido']].forEach(([key, label]) => { if (item.resultado?.[key] != null) fact(fields, label, readable(item.resultado[key])); });
        add(card, 'h4', 'Evidências declaradas pela extração');
        const evidence = item.resultado?.evidencias;
        if (!Array.isArray(evidence) || !evidence.length) empty(card, 'Nenhuma evidência registrada. Não há sustentação exibida para conferir as classificações.');
        else evidence.forEach(ev => {
          const node = add(card, 'div', null, 'evidence');
          if (!ev || typeof ev !== 'object') { add(node, 'p', readable(ev)); return; }
          add(node, 'strong', `Sustenta: ${readable(ev.sustenta)}`);
          if (ev.trecho_sustentacao) add(node, 'blockquote', ev.trecho_sustentacao);
          if (ev.campo) add(node, 'p', `Campo de origem: ${ev.campo}`);
          if (ev.referencia) add(node, 'p', `Referência: ${readable(ev.referencia)}`);
          if (ev.hash_conteudo) add(node, 'p', `SHA-256 informado: ${ev.hash_conteudo}`, 'muted');
          let target = null;
          if (ev.registro_id != null && data.registros_datajud.some(record => record.id === ev.registro_id)) target = `record-${ev.registro_id}`;
          if (ev.comunicacao_id != null && data.comunicacoes_pje.some(comm => comm.id === ev.comunicacao_id)) target = `communication-${ev.comunicacao_id}`;
          if (target) { const link = add(node, 'a', 'Conferir fonte neste processo'); link.href = '#' + target; link.addEventListener('click', event => { event.preventDefault(); const source = $(target); source.tabIndex = -1; source.querySelector('.document-body')?.setAttribute('open', ''); source.focus(); source.scrollIntoView(); }); }
          else empty(node, 'Fonte não resolvida neste contrato de API. Confira os identificadores no resultado completo; vínculo e citação não foram validados pela interface.');
        });
        add(card, 'h4', 'Lacunas apontadas pela IA');
        if (Array.isArray(item.resultado?.lacunas) && item.resultado.lacunas.length) { const gaps = add(card, 'ul', null, 'gaps'); item.resultado.lacunas.forEach(gap => add(gaps, 'li', readable(gap))); }
        else empty(card, 'Nenhuma lacuna informada nesta extração. Isso não comprova completude dos dados.');
        const technical = add(card, 'details'); add(technical, 'summary', 'Ver classificação, evidências e lacunas');
        add(technical, 'pre', JSON.stringify(item.resultado, null, 2));
      });
      const documentary = section(root, 'document-analysis', 'Análise documental PJe');
      add(documentary, 'p', 'Consultando disponibilidade da análise documental…', 'message');
      const review = section(root, 'review', 'Estado da revisão e inclusão na amostra');
      add(review, 'p', 'Revisão humana: comprovação indisponível neste endpoint.', 'review-state');
      add(review, 'p', 'A API não informa responsável, data, decisão de inclusão ou histórico de revisão humana. O status da extração e o campo revisao_humana não comprovam que alguém revisou o caso. Não há ação de aprovação disponível nesta tela.', 'muted');
      add(review, 'h4', 'Pendências para a pesquisa');
      const pending = add(review, 'ul', null, 'gaps');
      ['Confirmar pedido de concessão inicial e excluir revisão ou cessação.', 'Confirmar pertinência ao recorte territorial com evidência adequada; sede do órgão não é residência.', 'Conferir origem, conteúdo e limitações dos documentos antes de interpretar o resultado.'].forEach(text => add(pending, 'li', text));
      const chunks = add(root, 'details', null, 'section'); add(chunks, 'summary', `Trechos preparados para IA (${data.documento_chunks.length})`);
      if (!data.documento_chunks.length) empty(chunks, 'Nenhum trecho de publicação processado.');
      data.documento_chunks.forEach(item => { const card = add(chunks, 'article', null, 'entry'); add(card, 'p', `Publicação ${item.comunicacao_id} · trecho ${item.numero_chunk} · ${item.modelo_embedding} / ${item.versao_pipeline}`, 'muted'); add(card, 'div', item.texto, 'text'); });
    }
    async function loadDocumentAnalysis(number, request, includeText = false) {
      const root = $('document-analysis'); if (!root) return;
      root.setAttribute('aria-busy', 'true');
      try {
        const data = await get(`/admin/api/processos/${encodeURIComponent(number)}/analise-documental${includeText ? '?incluir_texto_local=true' : ''}`);
        if (request !== state.detailRequest) return;
        renderDocumentAnalysis(root, data, number, request);
      } catch (error) {
        if (request !== state.detailRequest) return;
        root.replaceChildren(); add(root, 'h3', 'Análise documental PJe');
        add(root, 'p', `Análise documental indisponível: ${error.message}. Isso não indica ausência de extrações.`, 'message error');
        const retry = add(root, 'button', 'Consultar disponibilidade novamente', 'secondary'); retry.type = 'button'; retry.addEventListener('click', () => loadDocumentAnalysis(number, request));
      } finally { if (request === state.detailRequest) root.setAttribute('aria-busy', 'false'); }
    }
    function renderDocumentAnalysis(root, data, number, request) {
      const textRetained = data.texto_retido !== false;
      root.replaceChildren(); add(root, 'h3', 'Análise documental PJe');
      add(root, 'p', 'Leitura de documentos próprios publicados no PJe. Extração automática não comprova validação humana ou inclusão definitiva na amostra.', 'muted');
      const status = add(root, 'div', null, 'facts'); fact(status, 'Revisão humana registrada', readable(data.revisao_humana)); fact(status, 'Revisão de privacidade', readable(data.revisao_privacidade));
      if (textRetained) {
        add(root, 'p', 'Resumos, narrativas e citações estão retidos por privacidade. A consulta abaixo solicita leitura local explícita; não executa IA nem autoriza envio externo.', 'notice');
        if (['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) { const button = add(root, 'button', 'Solicitar leitura local dos textos', 'secondary'); button.type = 'button'; button.addEventListener('click', () => { button.disabled = true; loadDocumentAnalysis(number, request, true); }); }
        else empty(root, 'Leitura textual disponível somente por acesso local autorizado pelo backend.');
      } else add(root, 'p', 'Leitura local solicitada. Conteúdo continua sujeito à revisão de privacidade; chamadas externas não são permitidas.', 'notice');
      add(root, 'h4', `Documentos próprios disponíveis (${(data.documentos || []).length})`);
      (data.documentos || []).forEach(doc => {
        const body = add(root, 'details', null, 'document-body');
        add(body, 'summary', `${doc.tipo_documento || 'Documento PJe'} · ID ${doc.documento_id || doc.id}`);
        add(body, 'p', `Fonte: ${doc.fonte || 'Não informada'} · ID local: ${doc.id} · SHA-256: ${doc.hash_conteudo || 'Não informado'}`, 'muted');
        if (!textRetained && typeof doc.texto === 'string') add(body, 'div', doc.texto, 'text');
        else empty(body, 'Texto retido por privacidade ou não disponibilizado pelo endpoint.');
      });
      if (!data.extracoes?.length) empty(root, 'Nenhuma extração documental registrada para este processo. Não há resumo documental gerado.');
      (data.extracoes || []).forEach(item => {
        const card = add(root, 'article', null, 'entry'); add(card, 'h4', 'Extração documental registrada');
        add(card, 'p', `Modelo ${item.modelo || 'Não informado'} · prompt ${item.versao_prompt || 'Não informado'} · ${when(item.criado_em)}`, 'muted');
        add(card, 'p', `Status de validação: ${item.status_validacao || 'Não informado'}`);
        const result = item.resultado || {};
        if (!textRetained && result.resumo_caso) add(card, 'div', result.resumo_caso, 'text');
        const fields = add(card, 'div', null, 'facts');
        if (!textRetained) [['provavel_causa', 'Provável causa'], ['ato_administrativo', 'Ato administrativo'], ['negativa_administrativa', 'Negativa administrativa'], ['requisito_controvertido', 'Requisito controvertido'], ['fundamento_judicial', 'Fundamento judicial']].forEach(([key, label]) => { if (result[key] != null) fact(fields, label, readable(result[key])); });
        if (result.desfecho && typeof result.desfecho === 'object') { fact(fields, 'Resultado sugerido', readable(result.desfecho.resultado)); fact(fields, 'Natureza da decisão', readable(result.desfecho.natureza)); fact(fields, 'Trânsito em julgado', readable(result.desfecho.transito_julgado)); }
        add(card, 'h4', 'Evidências documentais');
        if (!result.evidencias?.length) empty(card, textRetained ? 'Trechos retidos. Consulte a proveniência abaixo.' : 'Nenhuma evidência documental informada.');
        (result.evidencias || []).forEach(ev => {
          const node = add(card, 'div', null, 'evidence'); add(node, 'strong', `Sustenta: ${readable(ev.sustenta)}`);
          add(node, 'p', `Documento local ${ev.documento_id ?? 'Não informado'} · campo ${ev.campo || 'Não informado'} · intervalo Unicode [${ev.inicio ?? '?'}, ${ev.fim ?? '?'})`);
          add(node, 'p', `SHA-256: ${ev.hash_conteudo || 'Não informado'}`, 'muted');
          if (!textRetained && ev.trecho) add(node, 'blockquote', ev.trecho);
          const doc = (data.documentos || []).find(doc => doc.id === ev.documento_id);
          if (!textRetained && typeof doc?.texto === 'string' && Number.isInteger(ev.inicio) && Number.isInteger(ev.fim) && ev.inicio >= 0 && ev.fim > ev.inicio) {
            const codepoints = Array.from(doc.texto);
            const exact = ev.fim <= codepoints.length && codepoints.slice(ev.inicio, ev.fim).join('') === ev.trecho;
            add(node, 'p', exact ? 'Trecho coincide com o intervalo do texto recebido. Isso não valida a interpretação jurídica.' : 'Atenção: trecho não coincide com o intervalo do texto recebido.', exact ? 'muted' : 'error');
            if (ev.hash_conteudo && doc.hash_conteudo && ev.hash_conteudo !== doc.hash_conteudo) add(node, 'p', 'Atenção: o hash declarado na evidência difere da versão do documento recebido.', 'error');
            const body = add(node, 'details', null, 'document-body'); add(body, 'summary', 'Conferir texto de origem'); add(body, 'div', doc.texto, 'text');
          } else empty(node, 'Conferência de intervalo indisponível sem texto de origem.');
        });
        add(card, 'h4', 'Lacunas registradas');
        const gaps = add(card, 'ul', null, 'gaps'); (result.lacunas || []).forEach(gap => add(gaps, 'li', readable(gap)));
        if (!result.lacunas?.length) empty(card, 'Nenhuma lacuna exibida; isso não certifica completude.');
        const provenance = add(card, 'details'); add(provenance, 'summary', 'Modelo, versões e proveniência documental'); add(provenance, 'pre', JSON.stringify(item.proveniencia || {}, null, 2));
      });
      if (data.lacunas?.length) { add(root, 'h4', 'Disponibilidade e pendências'); const gaps = add(root, 'ul', null, 'gaps'); data.lacunas.forEach(gap => add(gaps, 'li', readable(gap))); }
    }
    $('filters').addEventListener('submit', event => { event.preventDefault(); state.offset = 0; loadList(); });
    $('previous').addEventListener('click', () => { state.offset = Math.max(0, state.offset - state.limit); loadList(); });
    $('next').addEventListener('click', () => { state.offset += state.limit; loadList(); });
    loadStats(); loadList();
    try { const number = decodeURIComponent(location.hash.slice(1)); if (/^(\d{20}|\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})$/.test(number)) loadDetail(number); } catch { $('detail-status').textContent = 'Referência de processo inválida na URL. Use a pesquisa.'; }
