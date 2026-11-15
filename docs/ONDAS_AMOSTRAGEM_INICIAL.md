# Ondas para finalizar a amostragem inicial

## Objetivo e coordenação

Entregar uma amostra operacional reproduzível de aproximadamente 200 processos únicos com documentos próprios e preparar 40 casos para revisão humana. Não é estimativa representativa de toda a população DataJud. Confirmação de concessão inicial e residência depende de evidência documental; sede do órgão não é residência.

Coordenação: Hermes, usando Orca. Run: `run_200e3f82033f`.

O snapshot informado pelo pesquisador é referência histórica. As contagens atuais e a elegibilidade serão auditadas em modo somente leitura. O plano de pesquisa (`plano.txt`) define o objetivo científico; `docs/CONTRATOS.md` rege persistência e proveniência. Divergências documentais devem aparecer na auditoria, não ser resolvidas por suposição.

## Onda 1 — quatro frentes paralelas já despachadas

| Responsável | Modelo/effort | Tarefa Orca | Entrega |
| --- | --- | --- | --- |
| Terra — amostragem e documentação | gpt-6.1-terra / medium | task_b0d53b4c6cfc | Inventário de todos os Markdown do projeto, síntese de intenção, auditoria real, manifesto estratificado de 200 processos e subconjunto de 40 |
| Luna — coleta dirigida | gpt-6-luna / medium | task_f4edc8a9d913 | Lote de até 60 candidatos ainda não consultados, equilibrado por Brasília/Formosa/Luziânia, em cópia SQLite nova |
| Sol — interface | gpt-6.1-sol / low | task_2a1471a8274b | Página integrada do processo, documentos, linha do tempo, extrações, evidências e pendência de revisão, validada em desktop/mobile |
| Sol — extração documental | gpt-6.1-sol / high | task_fe94eed42481 | Pipeline IpeaIA com rastreabilidade, citações exatas verificadas, abstenção, testes e preparação do piloto |

O frontend deve carregar as skills locais do Codex `$aura-asset-images`, `$visual-hierarchy`, `$tailwindcss`, `$responsive-design` e `$antiwebslop`, reportando indisponibilidades. Não se justifica migração de stack ou uso de imagens decorativas apenas para preencher a tela.

### Isolamento

As frentes compartilham o checkout, mas têm propriedade explícita de arquivos nos briefings Orca. Terra possui scripts de amostragem e sua documentação; Luna possui coletor/testes PJe e relatório de coleta; Sol frontend possui templates/static; Sol extração possui backend IA/prompts/testes e contrato de dados. Alterações cruzadas exigem coordenação.

Banco original preservado. Cada execução que precise gravar usa backup SQLite para um caminho novo. Não alterar `.env`, publicar dados pessoais, fazer commit/push, modificar submódulos ou contornar autenticação/CAPTCHA. Bronze e identidades documentais devem ser preservados.

## Onda 2 — integração e piloto documental

Depende da entrega do manifesto e do pipeline.

1. Verificar por código: unicidade dos 200 CNJs, elegibilidade territorial/institucional, assuntos, documentos próprios, IDs/hash, semente, quotas e determinismo.
2. Validar o lote de Luna por integridade/FKs, estados de consulta e associação documento–processo. Se for necessário incorporar novos documentos, usar consolidação para destino novo e regenerar manifesto com rastreabilidade. Não mudar silenciosamente o universo de uma amostra congelada.
3. Integrar contrato do backend à interface, executar testes de regressão e validar estados com e sem documentos/extrações.
4. Preparar e validar o piloto de 40 casos. Chamada real à IpeaIA depende de configuração e revisão de privacidade compatível com o plano, que prevê tratamento local de dados pessoais. Ausência de autorização comprovada bloqueia envio externo; não bloqueia dry-run, fila e testes locais.

## Onda 3 — revisão humana e gate de qualidade

O pesquisador revisa de 30 a 50 resultados (meta inicial: 40), conferindo campos, citações e vínculo com os documentos originais. Registrar correções separadas do resultado bruto e motivos de discordância; não marcar revisado automaticamente.

Medir por campo: sustentação da evidência, exatidão do trecho, classificação, omissões e abstenções apropriadas. Relatar numeradores/denominadores e erros por tipo documental/estrato. Critérios de aceitação para ampliar o lote devem ser definidos pelo pesquisador a partir desse piloto, não presumidos pelo modelo.

## Onda 4 — fechamento e ampliação condicionada

Após o gate humano, ajustar prompt/pipeline com nova versão, reavaliar os erros e ampliar aos demais casos aprovados. Entregar manifesto congelado, fila e registro de revisão, extrações efetivamente executadas, relatório de cobertura/lacunas e painel navegável. Sem petição inicial/processo administrativo, a causa pode permanecer indeterminada.

## Definição de concluído

- Manifesto real gerado e reproduzível; déficit explicitado se não houver 200 elegíveis.
- Subconjunto de revisão com documentos/evidências rastreáveis e estado pendente.
- Coleta finita com resultados reais ou bloqueio documentado.
- Pipeline e interface exercitados com testes reais, sem respostas artificiais apresentadas como IA executada.
- Revisão humana só conta quando efetivamente realizada pelo pesquisador.

O status das tarefas neste documento descreve o despacho inicial, não conclusão. A autoridade operacional de andamento e mensagens é o Run Orca; os relatórios de cada frente e verificações da coordenação registrarão o resultado final.

## Resultado da primeira rodada e correção de direção visual

- Terra entregou `data/amostragem-inicial/manifesto.json` e `.csv`: 200 processos únicos entre 843 elegíveis com documentos PJe próprios, de 3.823 candidatos. Brasília: 67; Formosa: 66; Luziânia: 67. Subconjunto `revisao_humana_40.json`/`.csv`: 40, todos pendentes. A coordenação conferiu unicidade, inclusão do subconjunto, registros TRF1/G1/JE e os 529 vínculos ID/hash dos documentos selecionados; todos conferiram. Cinco artefatos reproduzidos foram comparados byte a byte e coincidiram. Os estratos realizados têm 141 processos em 11946 e 59 em 11947; o único elegível classificado no estrato 6114 não entrou na seleção. Isso é limitação da composição realizada, não ausência de candidatos 6114 no banco.
- Luna encerrou o lote finito por divergência de identidade no cabeçalho documental. Dos 60 selecionados, um foi consultado e 59 permanecem pendentes; três documentos observados eram duplicados, zero documentos/vínculos novos. Não houve consolidação dessa cópia no original. Ver `docs/COLETA_PJE_AMOSTRA.md`.
- Sol backend entregou pipeline documental e fila local validada para 40 processos/113 documentos. Uma busca exclusivamente local recuperou 64 caminhos Bronze históricos, conferindo CNJ/ID/hash. Artefato final: `data/ia-documental/dry-run-20261029-02.json`; fila `fila-piloto-40-20261029-02.json`; relatório `RELATORIO_PIPELINE_20261029.md` na mesma pasta. Zero extrações persistidas e zero gerações externas. Credencial IpeaIA não configurada; privacidade e revisão humana pendentes.
- A coordenação executou a suíte Python ampliada: 211 testes passaram, com dois avisos de depreciação; `git diff --check` sem erro. Isso se refere ao estado anterior à segunda refação visual, que requer nova regressão.
- A primeira melhoria do frontend foi entregue e exercitada, mas o pesquisador rejeitou sua direção visual por ser incremental. Portanto, não é aceita como resultado final de design.

### Nova frente visual autorizada

Tarefa `task_5a2a097c3ee8`, dispatch `ctx_da44e782ebf4`, mesmo Sol 6.1 low com Full Access na sessão. O pesquisador escolheu **ferramenta de pesquisa contemporânea, estilo Linear, neutra, compacta, navegação lateral e foco no trabalho**. Escopo: refação integral das três telas (operações/coleta, processos e corpus documental), composição e sistema visual compartilhado; manter funcionalidades/APIs e privacidade. Sem instaladores, scripts remotos, CDN ou uploads. Exige verificação visual e funcional em todas as telas, desktop/tablet/mobile. Frente em andamento; não tratar a primeira entrega como aceite desta refação.
