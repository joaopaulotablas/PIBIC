# Auditoria da base atual — 3 nov. 2026

## Resumo executivo

A base já permite análises exploratórias sobre distribuição de processos, assuntos, tribunais, movimentações e contexto territorial. **Ainda não permite explicar com segurança por que cada processo foi judicializado nem medir seus desfechos**: não há extrações de IA nem revisões humanas gravadas, e só 1.025 dos 16.737 processos têm algum documento judicial externo vinculado (6,1%).

O principal limite agora não é falta de mais registros. É a distância entre o grande acervo de jurisprudência e os processos específicos do DataJud. Para avançar a análise, é preciso separar candidatos de casos confirmados, aproveitar os documentos já ligados, revisar as versões repetidas e registrar uma primeira camada de leitura humana/assistida com evidências rastreáveis.

## Escopo e método

- Banco examinado em modo somente leitura: `data/bpc-consolidado-luna-20261007.sqlite`.
- Integridade SQLite: `quick_check = ok`; nenhuma violação de chave estrangeira.
- Inventário textual local, sem IA ou classificação semântica, executado com o auditor já existente em `ingestion/src/bpc_ingestion/corpus_audit.py`. O JSON intermediário de 247 MB foi removido após consolidar as métricas agregadas neste relatório.
- A auditoria conta documentos, identificadores de origem, vínculos e disponibilidade de texto. “Pista lexical” significa apenas que uma expressão aparece no texto; não confirma pertinência, fundamento, pedido nem resultado.
- Esta fotografia reflete o banco local em 3 nov. 2026. Não foi feita coleta nova nem alteração de registros.

## O que há no banco

| Componente | Volume | Leitura correta |
|---|---:|---|
| Processos consolidados | 16.737 | Casos únicos na tabela principal |
| Registros DataJud | 16.796 | 59 registros a mais que processos; alguns processos têm mais de um registro |
| Movimentações | 907.521 | Histórico processual estruturado; não substitui o teor das decisões |
| Documentos públicos | 41.353 | Acervo de decisões, votos, ementas e outros documentos de várias fontes |
| Comunicações PJe | 302 | Comunicações processuais, não inteiro teor; ligadas a 171 processos |
| Vínculos documento–processo | 2.508 | Todos pelo critério `cnj_explicito`; os 2.508 vínculos conferem com o número CNJ associado |
| Processos com algum documento público vinculado | 1.025 (6,1%) | 15.712 processos não têm documento público externo vinculado |
| Extrações de IA / revisões humanas salvas | 0 / 0 | Nesta cópia do banco, ainda não há análise registrada no sistema |

Os dados processuais cobrem ajuizamentos de 22 fev. 2006 a 31 ago. 2026. Essa faixa é a data dos processos, não uma confirmação de que todos estejam atualizados até o fim do período.

### Assuntos: separar evidência direta de candidatos

| Código CNJ | Assunto | Processos que o têm | Com documento público vinculado |
|---:|---|---:|---:|
| 6114 | Benefício Assistencial (Art. 203, V, CF/88) | 405 | 11 |
| 11946 | Deficiente | 13.698 | 873 |
| 11947 | Idoso | 2.729 | 146 |

Os grupos se sobrepõem; não se devem somar as linhas como se fossem conjuntos independentes. O código 6114 é o sinal mais direto de BPC no assunto DataJud. “Deficiente” e “Idoso” são categorias amplas: indicam candidatos para triagem, mas não provam que o pedido seja BPC/LOAS. Essa distinção deve continuar explícita em qualquer painel, amostragem ou análise de IA.

### Cobertura por fonte documental

| Fonte | Documentos | Com texto principal | Processos com vínculo | Observação |
|---|---:|---:|---:|---|
| CJF/TRF1 | 18.535 | 18.535 | 61 | Acórdãos e decisões; 3.330 linhas excedentes por versões repetidas do mesmo ID de origem |
| PJe/TRF1 | 2.281 | 2.281 | 843 | Fonte mais útil para ler peças decisórias dos processos já associados |
| TRF6 | 9.359 | 9.359 | 123 | Jurisprudência pública; vínculos existentes são úteis, mas não representam todo o acervo |
| TRF4 | 5.518 | 5.518 | 0 | Sem vínculo a processo do DataJud nesta base |
| TRF2 | 3.111 | 3.111 | 0 | Sem vínculo a processo do DataJud nesta base |
| TRF5 | 1.351 | 1.351 | 0 | Sem vínculo a processo do DataJud nesta base |
| TNU | 766 | 766 | 1 | Inclui relatórios/votos e ementas; vínculo muito pequeno |
| STJ | 425 | 0 | 0 | Há ementa/espelho, mas não texto principal; sem vínculo a caso do DataJud |
| Arquivo TRF1 | 7 | 4 | 1 | Três registros sem texto principal |

Além desses documentos, há 302 comunicações PJe. Elas são úteis para observar atos de comunicação, mas não devem ser descritas como conteúdo integral ou decisão do processo.

No PJe/TRF1 há 816 despachos, 597 decisões, 785 sentenças e 78 acórdãos, além de cinco decisões monocráticas terminativas. Esse subconjunto — 843 processos associados — é o melhor ponto de partida para leitura de casos concretos. A tabela de tipos não prova que cada processo tenha todas as peças nem que a decisão disponível contenha a causa administrativa discutida.

## Achados de qualidade e limites

1. **Acervo não é cobertura por caso.** Há mais de 41 mil documentos, mas só 1.025 processos DataJud têm um documento público associado. Documentos sem vínculo podem servir como contexto jurisprudencial; não podem ser usados para afirmar o que aconteceu em um processo específico.
2. **Vínculos atuais são consistentes.** Os 2.508 vínculos registrados usam `cnj_explicito`; todos os números CNJ conferem com a lista CNJ do documento. Isso é uma boa base para enriquecer os vínculos, desde que se preserve o mesmo padrão verificável.
3. **Versões do CJF precisam de regra de canonicalização.** Há 18.535 linhas, mas 15.205 IDs de origem distintos; 3.034 IDs têm mais de um hash (até quatro versões do mesmo ID). As versões podem refletir atualização real ou diferenças de captura/normalização; é preciso compará-las antes de escolher uma versão canônica. Não tratar as 18.535 linhas como 18.535 decisões independentes.
4. **Duplicação textual exata é pequena.** O inventário encontrou 29 ocorrências excedentes de texto principal idêntico em 28 grupos. Isso é diferente da repetição de ID com hashes distintos descrita acima.
5. **Texto existe, mas não é sempre inteiro teor.** Há texto principal em 40.925 documentos públicos e nas 302 comunicações. Os 425 itens do STJ têm ementa/espelho, não texto principal; três itens do arquivo TRF1 não têm texto. A presença de texto tampouco certifica completude, OCR correto ou anonimização.
6. **Movimentação não equivale a motivação.** As 907.521 movimentações ajudam a reconstruir cronologia e atos, mas seus rótulos não explicam sozinhos o pedido, a negativa administrativa, a prova ou a razão da decisão.
7. **A base é geograficamente heterogênea.** Os registros incluem TRF1, TRF6 e TJGO, entre outros. Ao ampliar o recorte analítico, manter tribunal, grau, localidade e assunto como dimensões separadas; confirmar o significado de casos TJGO no recorte BPC antes de misturá-los com ações federais. Os maiores grupos observados incluem TRF1/JE (5.917), TJGO/G1 (4.502) e TRF6/JE (4.022).
8. **Dados agregados são contexto, não explicação individual.** Há 467 linhas de indeferimentos do INSS, 185 de concessões, 8.557 registros municipais de SUAS, 124 indicadores BPC municipais e 454 referências externas. Eles ajudam a contextualizar período/território, mas não estão ligados automaticamente à história administrativa de cada autor.
9. **A linguagem natural da IA ainda não está persistida nesta cópia.** Há zero linhas em `extracoes_ia` e zero em `revisoes_caso`. O resultado da conversa/teste da IpeaIA não aparece como dado salvo no banco examinado.

## Próximos passos recomendados — sem ampliar a coleta

1. **Formalizar estratos de análise**: (a) assunto direto 6114; (b) candidatos 11946; (c) candidatos 11947; (d) combinações entre eles. Não usar os grupos amplos como “casos BPC confirmados”.
2. **Começar pelo subconjunto com vínculo PJe/TRF1**. Criar uma fila de revisão com processo, documentos disponíveis, tipo/data, movimentações, assunto e fonte; preservar link e referência de página/trecho para cada observação. Não inferir causa se a peça não a explicitar.
3. **Revisar uma amostra estratificada e registrar no painel**: por assunto, tribunal/grau, ano/localidade e presença/tipo de documento. Registrar também “não foi possível determinar” e a razão. O objetivo inicial é medir qualidade e cobertura, não treinar ou avaliar um classificador ainda.
4. **Auditar versões CJF** por ID de origem e hash. Identificar se as mudanças alteram o conteúdo substantivo ou só a captura; então documentar a regra para escolher/mostrar versões, mantendo o histórico bruto.
5. **Apresentar cobertura e proveniência no painel**: distinguindo processo DataJud, documento ligado ao processo, jurisprudência contextual e comunicação PJe. Exibir claramente quando o painel não tem texto decisório.
6. **Depois da revisão piloto**, definir os campos de análise em linguagem natural — pedido, ato/negativa administrativa, motivo alegado, prova, fundamento judicial e resultado — cada um como “extraído”, “ausente” ou “incerto”, com citação documental e revisão humana. Só então rodar a IA em lote sobre documentos vinculados e medir concordância/erros.

## Decisão metodológica

**Há amostra suficiente para iniciar uma análise exploratória piloto; não há cobertura ou validação suficiente para concluir a causa de judicialização caso a caso, nem para generalizar os achados para todos os processos BPC.** O passo de maior valor é melhorar a ligação, revisão e interpretação do material já coletado, mantendo jurisprudência contextual separada de prova do processo individual.
