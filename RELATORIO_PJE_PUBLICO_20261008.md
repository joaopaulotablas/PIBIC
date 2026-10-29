# Conteúdo individual via PJe/TRF1 — 08/10/2026

## Atualização da coleta PJe — 12/10/2026

Além dos 50 CNJs históricos, foram consultados **90 CNJs inéditos**, em três
coortes reproduzíveis de 30, cada uma com dez por código de órgão DataJud
743/1798/2788 e ordenação SHA-256. Resultado agregado das coortes: 85 consultas
concluídas, uma `sem_documentos` e quatro interrompidas por divergência de
identidade. Foram acrescentados 207 documentos públicos verificados. Os
manifests completos estão em `data/pje-amostra-adicional30-20261012.json`,
`data/pje-amostra-adicional30-v2-20261012.json` e
`data/pje-amostra-adicional30-v3-20261012.json`; os arquivos `...lote...`
registram retomadas após parada por identidade.

Somando as duas rodadas de retomada: **140 CNJs selecionados**, 132 consultas
concluídas, uma sem documento-alvo e sete interrompidas por identidade;
acréscimo líquido de 320 documentos. PJe agora tem **523 documentos em 208
processos** (17 acórdãos, 139 decisões incluindo quatro monocráticas
terminativas, 156 despachos e 211 sentenças). Corpus geral: 1.058 documentos,
531 vínculos. Processos 16.737, registros DataJud 16.796, movimentos 907.521,
Comunica 220, extrações IA 0. SQLite íntegro, zero FK, zero vínculos PJe sem
critério CNJ e nenhuma coleta ativa. Nenhum processo novo foi criado.

Os textos são decisões/documentos publicados encontrados na consulta pública,
não autos completos. Seleção por assunto e órgão atual não comprova residência
DF/RIDE nem forma amostra estatística da população. Dados e Bronze continuam
locais, fora do Git e sem envio à IpeaIA. Divergências e limites estão
registrados abaixo; os manifests de candidatos não consultados dentro das
coortes não devem ser contados como resultados negativos.

## Retomada da amostra histórica — 12/10/2026

A retomada dos 50 CNJs do manifesto histórico terminou: **47 consultas
concluídas e três interrompidas pela validação de identidade documental**.
Dos casos concluídos, foram acrescentados 113 documentos HTML públicos
verificados; não houve criação de processos. Trinta e sete processos a mais
passaram a ter ao menos um documento PJe vinculado em relação à auditoria
anterior. PJe agora soma 316 documentos em 122 processos (12 acórdãos, 83
decisões — incluindo uma monocrática terminativa —, 102 despachos e 119
sentenças). Corpus geral: 851 documentos, 324 vínculos; processos 16.737,
registros DataJud 16.796, movimentos 907.521, comunicações 220 e extrações IA 0.

Três casos foram interrompidos quando o cabeçalho do documento não confirmou
o CNJ solicitado ou divergiu dele: `1001481-85.2020.4.01.3501`,
`1046112-92.2021.4.01.3400` e `1000391-83.2022.4.01.3400`. A validação é por
documento: qualquer documento correto já validado antes da interrupção fica
preservado; o documento cuja identidade falhou não é inserido nem vinculado.
Não se presumiu que a divergência fosse erro de digitação. As respostas brutas
ficam na Bronze local para auditoria. O manifesto histórico mantém os 50
selecionados; manifests de retomada em `data/` registram os lotes executados.

**Conferência:** `PRAGMA integrity_check=ok`, zero violações de chave estrangeira,
zero vínculos PJe cujo critério não inclua CNJ e nenhuma consulta PJe em execução.
As tabelas de processos, DataJud, movimentos, Comunica e extrações não foram
alteradas. O texto continua local, sem envio à IpeaIA, sem mudança de schema,
commit/push ou atualização do pacote remoto. Esta coleta é de documentos
publicados selecionados, não autos completos nem amostra representativa de
moradores DF/RIDE. A auditoria anterior abaixo fica preservada como histórico
do estado de 08/10/2026.

## Atualização — rodada histórica e encerramento desta tentativa

O PJe agora contém **203 documentos válidos, vinculados a 85 processos**:
80 sentenças, 52 decisões, 65 despachos e seis acórdãos. A rodada histórica
acrescentou 45 textos em 12 processos de 2020–2022 (12 sentenças, 11 decisões,
20 despachos, dois acórdãos). Corpus total: 738 documentos e 211 vínculos.
Processos/DataJud/movimentos/comunicações/extrações permaneceram inalterados.

**Interrupção por divergência real de identidade:** no processo solicitado
`1001481-85.2020.4.01.3501`, o link publicado do documento `469433861` abriu
texto com cabeçalho `1001906-15.2020.4.01.3501`. Não foi tratado como erro de
digitação, precedente ou documento do processo solicitado. Esse documento
ficou apenas na Bronze, foi rejeitado e não existe na Silver. Um despacho
anterior do caso, corretamente identificado, permanece salvo. O lote parou
nesse ponto, conforme a instrução de interromper quando não der certo; não
foi retomado nem ampliado após a confirmação dessa divergência.

Manifesto: `data/pje-historico50-de4fac67cd8144b3a618ad2917f5dfd6.json`.
Seleção por assunto/grau/sigilo e órgão segue o contrato; anos e grupos de
órgão foram alternados com semente `pje-historico-20261008-v1`. Dos 50
selecionados, 12 foram consultados: 11 concluídos e um parcial com falha.
Os outros **38 não foram consultados**, e não são resultados vazios.
Esse encerramento não significa que os portais ou todos os casos disponíveis
foram esgotados, nem ausência de decisões nos casos ainda pendentes.

Totais acumulados: 88 CNJs consultados, 83 concluídos, três sem documento
alvo e dois parciais com documento rejeitado. São 85 com ao menos um texto;
15 execuções históricas falhas permanecem preservadas. Não somar execuções
de retomada para contar documentos ou casos.

| Origem CNJ | Casos com texto | Documentos |
| --- | ---: | ---: |
| 3400 — Brasília | 29 | 77 |
| 3506 — Formosa | 28 | 74 |
| 3501 — Luziânia | 25 | 44 |
| 3500 — Goiânia | 2 | 4 |
| 4300 — Tocantins | 1 | 4 |

82 casos têm numeração das três sedes principais; três têm origem fora
delas e foram selecionados pelo órgão atual DataJud. Nada disso comprova
residência DF/RIDE. Nenhum processo novo foi criado.

Correções de parser foram limitadas a estruturas observadas: `PROCESSO N.`,
bloco recursal SJDF e bloco institucional próprio de recurso JEF depois do
voto. Campo `strong` único, bloco institucional exato, CNJ completo e ID da
assinatura continuam obrigatórios nesse último formato; número avulso no
voto ou bloco citado em `blockquote` não comprova identidade. Teste adicional
confirma que um documento com outro CNJ interrompe o lote, não é salvo e
não apaga o documento válido importado antes dele.

**Verificação final:** 183 testes passaram; SQLite íntegro, zero violações
de FK e nenhuma coleta PJe em execução. Todos os 203 documentos foram
reprocessados da Bronze, com payload/hash/identidade/vínculo conferidos;
538 gzip da fonte íntegros. Auditorias locais imutáveis:

- `data/auditoria-pje-historico-20261008-6e0e7edb080547deb8b19638c902ba87.json`;
- `data/auditoria-corpus-20261008-com-pje-historico-v1.json`: 958 itens,
  937 textos principais distintos. Pistas lexicais não são classificações.

A decisão para NLP/Métricas continua: **PJe público é fonte viável de texto
individual verificado**, além de atos publicados do Comunica. Não são autos
completos e os textos não entram automaticamente na triagem de metadados.
Dados continuam locais, fora do Git e sem envio à IpeaIA; pacote remoto
anterior não foi atualizado. Abaixo está preservado o registro da primeira rodada.

## Primeira rodada — resultado e decisão para NLP/Métricas

A consulta pública PJe/TRF1 funcionou: 158 documentos HTML publicados foram
salvos e vinculados a 73 processos já existentes. A fonte de conteúdo individual
agora inclui `pje_trf1`, além das comunicações/atos publicados do Comunica.
Não dependemos exclusivamente do CRPS; este é administrativo e permanece separado.
Isso não significa autos completos, acesso a documentos restritos ou confirmação
automática de BPC/concessão inicial/residência/desfecho.

Os novos textos NÃO entram automaticamente na triagem de metadados IpeaIA.
Continuam locais, com revisão de privacidade pendente. A etapa seguinte de
interpretação precisa consumir documentos por processo, preservar evidências
e distinguir pedido, fundamento administrativo e resultado de cada ato.

## O que entrou

Banco alterado: `data/bpc-consolidado-luna-20261007.sqlite`.

| Item | Antes | Depois |
| --- | ---: | ---: |
| Processos | 16.737 | 16.737 |
| Registros DataJud | 16.796 | 16.796 |
| Movimentos | 907.521 | 907.521 |
| Documentos públicos | 535 | 693 |
| Vínculos documento/processo | 8 | 166 |
| Comunicações | 220 | 220 |
| Extrações IA locais | 0 | 0 |

Documentos novos: 68 sentenças (24 tipo A, 17 tipo B, 27 tipo C), 41 decisões
(40 “Decisão”, uma monocrática terminativa), 45 despachos e quatro acórdãos.
Os tipos são os rótulos do portal, não classificação do resultado judicial.

Distribuição pelo código de origem do número CNJ:

| Origem | CNJs com texto | Documentos |
| --- | ---: | ---: |
| 3400 — Brasília | 25 | 55 |
| 3506 — Formosa | 25 | 67 |
| 3501 — Luziânia | 21 | 30 |
| 3500 — Goiânia | 1 | 2 |
| 4300 — Tocantins | 1 | 4 |

Seleção usa códigos de órgão atuais DataJud 743/1798/2788 e assuntos
6114/11946/11947, graus G1/JE e sigilo zero/nulo. Códigos locais não são
códigos IBGE de sete dígitos. Órgão atual, origem do número e residência são
conceitos diferentes: dois candidatos têm origem fora das três sedes principais.
Não promover os 73 automaticamente a amostra de moradores DF/RIDE.

## Como foi obtido

Página oficial:
https://pje1g-consultapublica.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam

O botão chama `executarReCaptcha`, que nesta página publica CAPTCHA desativado
(`if (false)`). A pesquisa normal é a ação AJAX de `executarPesquisa`, não o ID
aparente do botão. O cliente acompanha cookies/ViewState apenas da sessão
pública e segue os links `openPopUp` publicados no resultado. Não inventa IDs
ou valores `ca`, não faz login nem resolve/altera CAPTCHA. Se a proteção mudar,
para antes da pesquisa.

Valida resultado CNJ único, número rotulado no detalhe, cabeçalho do documento
e ID na assinatura. Formatos de cabeçalho observados estão no CONTRATOS.md.
Cabeçalho estruturado tem prioridade sobre precedentes citados no corpo.
O primeiro piloto falhou em um documento sem qualquer CNJ; esse documento
continua excluído e a consulta parcial continua marcada `falhou`.

Cada resposta fica em gzip imutável antes do parser. Texto vem de `.folha`,
sem scripts/estilos/interface de download. Data de juntada não vira data de
decisão: datas projetadas permanecem nulas. Certidões/petições não são importadas.
Nesta versão são consultados apenas os documentos alvo da primeira página,
com limite de dez por processo. Não baixa PDF nem afirma cobertura completa.

## Amostragem e retomadas

76 CNJs distintos foram efetivamente consultados. Último estado por CNJ:
72 concluídos, três sem documentos alvo e um parcial com uma decisão válida
salva antes de rejeitar o documento sem CNJ. Os 73 com algum texto incluem
esse caso parcial. Onze execuções históricas com falha permanecem preservadas;
dez delas foram superadas por novas consultas após correções de layout.
Contar apenas execuções finais, não somar registros das retomadas.

Depois do piloto foram concluídos dois manifestos de anos 2023/2024/2025,
alternando os três grupos de órgão e ordenação determinística por SHA-256:

- `data/pje-amostra-recente-9a642fcbe54847e692db7e951a1332d2.json`: 20 casos,
  18 concluídos e dois sem documentos alvo.
- `data/pje-ampliacao50-f0e38a4f8e664a8398e74d9c7e1a4e75.json`: 50 casos,
  49 concluídos e um sem documentos alvo.

Não é uma estimativa representativa da população nem censo. Ainda há casos
pendentes fora desses lotes. Falha/bloqueio interrompe cada lote; retomada exige
inspeção da causa e não sobrescreve documentos ou execuções anteriores.

## Exemplo que melhora o entendimento

No processo `1053078-37.2022.4.01.3400`, documentos locais 536/537 (sentença
1385198841 e despacho 1313072753), a sentença informa discussão sobre demora
no julgamento de recurso administrativo. O dispositivo indefere a inicial
e extingue sem resolução do mérito. Isso esclarece o motivo do acesso ao
Judiciário sem confundi-lo com negativa judicial de concessão de BPC.
Não foi alterado o resultado antigo da triagem IA nem criada extração automática.

## Outras fontes tentadas

Comunica continuou respondendo HTTP 503/manutenção; não foi ampliado o lote.
CJF/JEF1: dez novos CNJs consultados, nenhum documento obtido. Ausência na
pesquisa não prova ausência de sentença nos autos.

A [página oficial de diários do TRF1](https://www.trf1.jus.br/trf1/diarios-da-justica/diarios-da-justica)
continua separando DJEN judicial, atos administrativos e acervos históricos.
Novas tentativas nos links históricos: e-DJF1/2015–2020 retornou 502;
2009–2015 expirou; biblioteca de 1990–2008 rejeitou a requisição. Nenhum
diário foi importado nem atos administrativos confundidos com texto judicial.
CRPS e pedido institucional permanecem pendentes; nenhuma solicitação foi enviada.

## Verificação e uso

181 testes passaram (dois avisos de depreciação existentes). SQLite:
`integrity_check=ok`, nenhuma violação de FK e nenhuma coleta PJe em execução.
Todos os 158 documentos foram reprocessados da Bronze com o parser final;
payload/hash, CNJ, ID e vínculo foram conferidos. Todos os 439 gzip da fonte
foram lidos com validação de integridade.

Auditorias locais, sem texto pessoal no relatório:

- `data/auditoria-pje-20261008-09417c3c70df45de8e9182b9f8f09171.json`;
- `data/auditoria-corpus-20261008-com-pje-v1.json`: 913 itens no corpus total,
  892 textos principais distintos. Pistas lexicais não são conclusões por caso.

Retomar o manifesto concluído é idempotente:

```powershell
.\.venv\Scripts\python.exe -m bpc_ingestion.pje_public --database-url sqlite:///data/bpc-consolidado-luna-20261007.sqlite --limit 50 --manifest data/pje-ampliacao50-f0e38a4f8e664a8398e74d9c7e1a4e75.json
```

O painel de documentos tem filtro “PJe — TRF1 consulta pública”; mostra
metadados e retém texto/links enquanto a privacidade está pendente.
Os arquivos `data/` permanecem fora do Git. O pacote remoto antigo NÃO foi
atualizado: um `git pull` não leva os novos textos ao servidor IpeaIA.
Sem commit/push, alteração do submódulo, migração ou chamada externa à IpeaIA.
