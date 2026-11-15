# Da coleta à análise dos casos BPC

Documento de leitura e decisão — 03/11/2026.

## 1. Temos dados suficientes?

**Sim, para começar um piloto de interpretação documental e avaliar sua qualidade.** Ainda não sabemos se temos evidência suficiente para explicar a judicialização em todos os casos ou produzir estimativas representativas da população.

O objetivo do estudo é analisar ações de concessão de BPC no TRF1, no recorte DF/RIDE. Os assuntos CNJ selecionam candidatos; a confirmação de concessão inicial depende da leitura dos documentos. Revisão e restabelecimento/cessação precisam ser identificados e separados conforme o escopo vigente.

Não é necessário concluir toda a coleta para iniciar a análise. O piloto deve revelar quais informações os textos realmente contêm e quais documentos ainda precisamos buscar.

## 2. O que já existe

Contagens da última conferência do banco consolidado, cuja última alteração registrada é de 15/10/2026. Não representam uma nova coleta em novembro.

| Material | Quantidade | Utilidade para a pesquisa |
| --- | ---: | --- |
| Processos únicos | 16.737 | Cadastro amplo de candidatos, incluindo grupos suplementares fora do recorte principal |
| Registros DataJud | 16.796 | Classe, assuntos, grau, órgão e datas; um processo pode ter mais de um registro |
| Movimentações | 907.521 | Cronologia e eventos processuais |
| Documentos públicos e versões | 41.353 | Textos dos casos e jurisprudência complementar |
| Vínculos documento–processo | 2.508 | Associação explícita a 1.025 processos existentes |
| Documentos PJe/TRF1 | 2.281 | Textos próprios de 843 processos, principal insumo para o piloto |
| Sentenças PJe/TRF1 | 785 | Possíveis relatos do pedido, controvérsia, fundamentação e resultado |
| Comunicações PJe | 302 | Atos publicados de 171 processos |
| Extrações IA na cópia consolidada conferida | 0 | Resultados do servidor remoto precisam ser conferidos/importados separadamente |

A auditoria local documentada em `docs/AMOSTRAGEM_INICIAL.md` já registra 3.823 candidatos principais, 843 com documentos próprios e um manifesto de 200 processos selecionados. Entre os 200, 189 têm documento rotulado como sentença, decisão ou acórdão e 11 não têm esses rótulos. Isso não confirma resultado nem elegibilidade final. Há também uma subamostra de até 40 para revisão.

Essa seleção já pode ser aproveitada: primeiro validar o manifesto e sua correspondência com o banco; depois usar a subamostra de 40 para o piloto. Não é necessário criar uma seleção concorrente de 50 sem justificar a mudança.

## 3. Como cada base contribui

| Fonte | Contribuição | Limite principal |
| --- | --- | --- |
| DataJud e TPU/CNJ | Encontrar candidatos, organizar assuntos e reconstruir eventos | Metadados não explicam, sozinhos, o motivo individual |
| PJe público TRF1 | Ler sentenças, decisões, despachos e acórdãos dos casos existentes | Disponibilidade parcial; sem garantia de autos completos |
| Comunica/DJEN | Recuperar atos e publicações adicionais | Publicação não equivale ao conjunto de peças |
| CJF/TRF1, TNU, STJ e TRF2/4/5/6 | Comparar argumentos e construir categorias jurídicas | Documento complementar só explica um caso quando há vínculo documental comprovado |
| INSS: indeferimentos e concessões | Contextualizar motivos e comportamento administrativo agregado | Não identifica a negativa administrativa de cada litigante |
| CGU: BPC municipal | Contextualizar estoque e valores de benefícios | Não identifica requerentes judiciais |
| MDS/SUAS e VIS DATA | Contextualizar atendimento socioassistencial e séries administrativas | Agregados não demonstram condições individuais |
| IBGE/SIDRA | Contextualizar idade, deficiência e renda municipal | Estatísticas municipais não são perfil dos autores |
| CRPS | Possível fonte adicional de fundamentos administrativos | Importação analítica e vínculo com os casos ainda precisam ser demonstrados |

## 4. O que queremos extrair de cada caso

O resultado deve permitir responder, com linguagem natural e evidências:

1. O processo trata de concessão inicial de BPC? Há revisão, restabelecimento ou outro objeto?
2. O que foi pedido e qual situação o documento relata?
3. Há motivo explícito de negativa, demora ou outra conduta administrativa?
4. Qual requisito foi discutido: deficiência, impedimento de longo prazo, renda, idade ou outro?
5. Qual fundamento o juízo adotou e qual resultado o documento registra?
6. Quais informações continuam ausentes ou contraditórias?

Para cada afirmação relevante, preservar documento de origem, identificador, hash e trecho literal verificável. Distinguir relato da parte, informação administrativa relatada e conclusão judicial. Quando o texto não responder, registrar “não identificado”.

Exemplo de formato de leitura, meramente ilustrativo: “O documento relata pedido de concessão de BPC e controvérsia sobre o requisito de deficiência. O motivo administrativo específico não foi identificado no texto disponível.” O sistema só deve produzir isso quando as evidências do caso sustentarem a descrição.

Este documento define objetivos de leitura, não cria um schema. Campos, versões e persistência seguem `docs/CONTRATOS.md`; qualquer alteração estrutural deve ser registrada ali.

## 5. Sequência de entregas

| Etapa | Entrega verificável | Quando avançar |
| --- | --- | --- |
| 1. Conferir a amostra existente | Manifesto de 200 validado, subamostra de 40 e documentos localizados | Identidades, recorte e disponibilidade conferidos |
| 2. Ler dez casos | Categorias iniciais e exemplos de informação disponível/ausente | Categorias compreensíveis e sustentadas pelos textos |
| 3. Integrar o piloto documental | Entradas preparadas, extrações versionadas e trechos conferidos | Pipeline validada e ambiente IpeaIA pronto para o tratamento previsto |
| 4. Analisar e revisar 40 casos | Resultados da IA e correções humanas registradas separadamente | Erros e abstenções medidos por campo |
| 5. Ajustar e ampliar para 200 | Lote analisado com a versão aprovada e relatório de cobertura | Critérios de qualidade definidos e aceitos pelo pesquisador |
| 6. Coletar por lacuna | Documentos adicionais dos casos que ficaram sem resposta | Coleta responde a uma necessidade observada na análise |

Já existem alterações locais de amostragem, pipeline documental e interface. São trabalho em andamento: sua presença no checkout não comprova integração, teste ou execução real da IA. A próxima implementação deve começar pela revisão dessas entregas, evitando refazê-las.

## 6. Como o painel deve funcionar

O painel deve apoiar a leitura e a revisão da pesquisa. A tela principal precisa mostrar a fila de casos e permitir filtrar por sede, assunto, ano, disponibilidade documental, processamento e revisão.

Ao abrir um processo, o pesquisador deve encontrar:

- resumo natural e situação de inclusão no estudo;
- pedido, motivo administrativo relatado, controvérsia e resultado identificado;
- documentos originais e evidências ao lado de cada conclusão;
- linha do tempo processual;
- informações ausentes e divergências;
- ação para confirmar ou corrigir a análise, com histórico da revisão.

As contagens mais úteis são: candidatos, casos com documentos, casos preparados, analisados, revisados, incluídos e excluídos. A quantidade total de documentos continua disponível como informação de cobertura.

Primeira entrega de interface: um fluxo completo e verificável de abrir caso → ler documento → conferir evidência → registrar revisão. Uma reformulação visual ampla vem depois desse fluxo funcionar.

## 7. Como avaliar o piloto

Registrar por campo a quantidade de respostas corretas, incorretas, ausentes e de abstenções apropriadas. Conferir se as citações existem e se realmente sustentam as conclusões. Medir também o tempo de revisão por caso.

Separar duas perguntas: “a IA interpretou corretamente o texto?” e “o texto permite responder à pergunta de pesquisa?”. Uma resposta indeterminada pode estar correta quando faltam peças.

O piloto permite avaliar viabilidade e melhorar o método. Estimar frequência das causas ou taxa de procedência exige população final definida, desenho amostral adequado e denominadores explícitos. A seleção atual depende da disponibilidade documental e não sustenta, por si, generalização populacional.

## 8. Prioridade proposta

Começar pela integração e avaliação dos 40 casos já previstos, com leitura inicial de dez e uma página de revisão utilizável. A meta é produzir casos interpretados e conferidos, categorias fundamentadas e uma lista objetiva das lacunas. A coleta direcionada do TRF1 passa a suprir essas lacunas.

Referências locais: `docs/CONTRATOS.md`, `docs/ESCOPO_PESQUISA.md`, `docs/AMOSTRAGEM_INICIAL.md`, `docs/ONDAS_AMOSTRAGEM_INICIAL.md` e `docs/FONTES_ABERTAS.md`.
