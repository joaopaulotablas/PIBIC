# Frontend de pesquisa: entrega e validação

Data: 29/10/2026. Task `task_2a1471a8274b`, dispatch `ctx_58dbdc8da7fe`.

## Entrega

`ingestion/src/bpc_ingestion/static/processos.html` mantém HTML/CSS/JS e os fluxos de busca, filtros, paginação e retorno à coleta. Dossiê com capa DataJud, timeline cronológica com origem por registro, publicações expansíveis, documentos próprios separados do corpus complementar, resumo de IA, campos analíticos, evidências ligadas à fonte e lacunas legíveis. Payload original e resultado completo continuam disponíveis em áreas expansíveis.

Hierarquia com coluna maior para leitura, fonte serif local no texto jurídico, medida de leitura, redução de bordas e sombras, seleção identificada por `aria-pressed`, skip link, status anunciados, foco visível e reflow mobile. Seleção por teclado transfere foco para o dossiê; links internos mantêm o CNJ da URL. Respostas obsoletas não substituem uma seleção nova. Erros oferecem nova consulta e não são apresentados como ausência de dados.

Integração: `GET /admin/api/processos`, `GET /admin/api/processos/{CNJ}`, `GET /resumo` e nova rota do worker backend `GET /admin/api/processos/{CNJ}/analise-documental`. Textos documentais ficam retidos por padrão; botão local solicita `?incluir_texto_local=true`, sem executar modelos. Ausência do flag de privacidade mantém retenção. Comparação de citações usa codepoints Unicode, limite exclusivo e teste de limites; coincidência textual não certifica interpretação jurídica ou revisão humana. Não existe ação de aprovação humana.

## Arquivos desta frente

- `ingestion/src/bpc_ingestion/static/processos.html`
- `ingestion/src/bpc_ingestion/static/DESIGN.md`
- `ingestion/tests/frontend/processos.browser.js`
- `ingestion/tests/frontend/artifacts/.gitignore`
- Este relatório.

Nenhum backend Python, schema, `.env`, submódulo ou arquivo de outra frente foi editado. Alterações desses arquivos visíveis no checkout pertencem aos demais agentes.

## Banco e execução local

Original aberto somente leitura com `sqlite3` URI `mode=ro`. Backup SQLite novo, sem sobrescrever: `data/bpc-frontend-fc0ad14c187a474db9b555bbc3fa8b60.sqlite`; `PRAGMA quick_check` retornou `ok`. O servidor desta frente seleciona explicitamente essa cópia por variável de processo, sem alterar `.env`.

Servidor disponível para inspeção da coordenação em `http://127.0.0.1:8766/admin/processos`, iniciado com `.venv/Scripts/python.exe -m uvicorn bpc_ingestion.api:app --host 127.0.0.1 --port 8766`. Reiniciado uma vez após implementação da nova rota. Nenhuma coleta, importação de resultado sintético ou chamada de IA externa foi executada.

## Resultados reais

| Verificação | Resultado |
| --- | --- |
| `python -m unittest discover -s ingestion/tests -p test_admin_processes.py` | 4 testes passaram |
| `python -m unittest discover -s ingestion/tests -p test_dashboard.py` | 5 testes passaram |
| `processos.browser.js` executado no navegador Orca local | 17 verificações passaram |
| `node --check` do script inline e teste de navegador | Passou |
| `git diff --check` do HTML | Passou |
| Nova rota documental em processo com documentos próprios | HTTP 200, `Cache-Control: no-store` |
| Resposta padrão documental | Texto retido, documentos com `texto=null` |
| Opt-in local, backend e UI reais | Dois documentos próprios legíveis, zero extrações documentais explicitado |
| 1440×900 | Duas colunas, sem overflow horizontal |
| 768×1024 | Uma coluna, sem overflow horizontal |
| 390×844 | Uma coluna, sem overflow horizontal, foco transferido ao dossiê |
| Tecla Tab no navegador Orca | Foco em link, outline de 3px |

As 17 verificações sintéticas cobrem estados vazios, ausência de revisão humana mesmo com status de extração validado, HTML não executado, protocolo inseguro bloqueado, retenção de texto, ausência do flag de privacidade, ordem temporal, evidência ligada ao registro, lacunas fora do JSON, opt-in explícito, offsets Unicode com emoji, limites inválidos, trecho divergente, erro de endpoint com retry e resposta atrasada. Fixtures ficam apenas no DOM; não foram persistidas. Para repetir, carregar a página local e executar o conteúdo de `processos.browser.js` com `orca eval --expression` na aba de teste.

## Capturas e limites

Capturas permanecem locais em `ingestion/tests/frontend/artifacts/`, ignoradas pelo Git, sem upload. `desktop-1280-local.png` e `mobile-local.png` foram inspecionadas visualmente. `desktop-local.png` (1440×900) e `tablet-local.png` (768×1024) mostram repetição do compositor na faixa que excede o tamanho físico do painel Orca; a medição DOM dos viewports não apontou overflow. A captura desktop de 1280×900 evita essa falha do compositor. Não houve teste em aparelho físico ou auditoria WCAG completa.

`slop-lint` apontou zero erros, seis avisos de borda lateral e um informativo sobre três colunas. Bordas são usadas para aviso real, seleção, separação de texto documental, sequência temporal e evidência citada, conforme DESIGN.md. Três colunas referem-se às contagens existentes no breakpoint tablet, não a cards decorativos. A borda decorativa nas contagens foi removida.

Cinco skills solicitadas disponíveis e consultadas: aura-asset-images, visual-hierarchy, tailwindcss, responsive-design e antiwebslop. Sem imagens decorativas, CDN, downloads ou novas dependências. CSS nativo preservado porque não existe pipeline Tailwind no painel.

## Pendências científicas e humanas

Esta cópia não contém extrações do novo tipo documental. Sua renderização com extração foi exercitada por fixture sintética; o estado real testado foi a ausência de execução. Revisão humana, revisão de privacidade e inclusão definitiva na amostra permanecem pendentes, sem promoção automática. Não há bloqueio técnico restante para esta frente; decisões científicas continuam com o pesquisador e a coordenação.
