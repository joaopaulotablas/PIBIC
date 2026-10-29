# Fontes abertas adicionais — avaliação inicial (22/09/2026)

O recorte principal continua sendo o de [ESCOPO_PESQUISA.md](ESCOPO_PESQUISA.md).
Estas fontes não substituem o DataJud e não devem ser ligadas a uma pessoa ou
processo sem identificador e autorização adequados.

## DJEN / Comunica PJe

- Retomada do manifesto `data/manifesto-comunica-luna-400-20261008.csv` em
  13/10/2026: 400/400 CNJs consultados sem autenticação, em três grupos (200
  núcleo Brasília, 100 Formosa e 100 Luziânia). A API respondeu HTTP 200 em
  todos; 41 processos tiveram publicações (31/200 Brasília, 4/100 Formosa,
  6/100 Luziânia) e 359 retornaram sem resultado. Foram acrescentadas 82
  comunicações, elevando o total local de 220 para 302. O recorte é uma amostra
  estratificada, não representativa; “sem resultado” significa ausência no
  Comunica, não inexistência de atos ou autos. Bronze íntegra (389 respostas na
  execução principal, SHA-256 `b1e59dfc738d7057d728c903bb3644ef76e707ae6934458e5619e26d3a4a45b4`),
  banco íntegro e sem duplicatas. Backup pré-coleta:
  `data/backup-pre-comunica-djen-20261012.sqlite`. Detalhes e limitações em
  `RELATORIO_COLETA_COMUNICA_DIARIOS_LUNA.md`.
- A consulta pública `GET /api/v1/comunicacao` por número CNJ, já implementada,
  respondeu sem autenticação. No piloto de 50 processos ainda não consultados,
  estratificados em 10 por ano de ajuizamento de 2021 a 2025 no recorte
  TRF1/órgão de Brasília/G1 ou JE, 3 tiveram resultado e 47 não tiveram.
  Foram persistidas 7 comunicações (intimações, despacho e ato ordinatório),
  nenhuma tipificada como sentença. O piloto não estima cobertura universal.
- A [API pública documenta](https://hcomunicaapi.cnj.jus.br/swagger/djen.yml)
  busca por tribunal, data e texto, além do caderno por tribunal/data/meio.
  A consulta experimental de texto `BPC` retornou HTTP 500; não foi usada
  para ingestão. Um caderno TRF1/D de 21/09/2026 respondeu sem credencial,
  mas anuncia 51.030 comunicações e 197.903.371 bytes. A ingestão indiscriminada
  de cadernos inteiros não se justifica antes de medir a cobertura e o custo.
- Comunicações são atos publicados, não inteiro teor dos autos. O endpoint
  `POST` e a autenticação do CNJ são de uso dos tribunais, não deste projeto.

## TRF1

- A [consulta processual antiga](https://processual.trf1.jus.br/consultaProcessual/)
  apresenta metadados e, em alguns processos, links de “Inteiro Teor”. Uma
  tentativa de consulta automatizada de um processo de 2018 do nosso recorte
  recebeu a página de verificação anti-robô. Não contornar essa proteção.
- O [PJe atual](https://www.trf1.jus.br/trf1/processual/consulta-processual)
  limita a consulta pública, e não foi identificada API pública de coleta em
  lote de sentenças. Acesso sistemático a documentos exige diálogo institucional
  com o tribunal. Uma amostra manual autorizada pode medir a disponibilidade.

## INSS — bases mensais

- O catálogo oficial [CKAN do INSS](https://dadosabertos.inss.gov.br/) responde
  sem credencial. As buscas por “beneficios indeferidos” e “beneficios concedidos”
  catalogaram respectivamente 102 e 106 recursos nesta rodada. Esses números
  contam metadados de arquivos, não benefícios importados. A tabela
  `recursos_externos` contém o catálogo e mantém URL e metadados da fonte.
- No arquivo [Benefícios Indeferidos — julho/2026](https://dadosabertos.inss.gov.br/dataset/beneficios-indeferidos-plano-de-dados-abertos-jun-2023-a-jun-2025),
  a leitura experimental encontrou 935.123 linhas. Para `UF = Distrito Federal`,
  foram 5.200 indeferimentos da espécie 87 (BPC pessoa com deficiência) e 462
  da 88 (BPC idoso). Há coluna de motivo, mas não de número CNJ nem município
  de residência nessa planilha. Esses totais **não** representam processos nem
  requerentes únicos e não devem ser comparados diretamente à amostra DataJud.
  Não houve persistência de microdados; a cópia temporária foi removida.
- Próxima implementação: importador de indicadores agregados por competência,
  UF, espécie e motivo, com hash e URL do arquivo de origem, dicionário de
  categorias e controle de qualidade. Criar o contrato da nova tabela antes da
  migração. Para análise municipal, usar fonte que explicite a geografia e sua
  unidade (residência, APS ou município pagador).

## Portal da Transparência/CGU — integrado

- O pesquisador configurou localmente o token da
  [API do Portal da Transparência](https://portaldatransparencia.gov.br/api-de-dados).
  Ele permanece no `.env` e não deve ir ao Git nem a mensagens. A coleta usa
  `GET /api-de-dados/bpc-por-municipio` com `mesAno`, `codigoIbge` e `pagina`,
  autenticado pelo cabeçalho `chave-api-dados`.
- Uma chamada real para Brasília (`5300108`) em julho/2026 retornou
  `quantidadeBeneficiados = 70480` e `valor = 131276767.55`, além de
  `dataReferencia`, município e tipo BPC. O comando `transparencia-bpc` grava
  a resposta original na Bronze e o indicador em `indicadores_bpc_municipio`.
  A série de Brasília de janeiro/2019 a julho/2026 foi coletada: 91 competências,
  todas com resposta, e uma reexecução não duplicou a competência já existente.
  Esses dados são agregados mensais; não representam novas concessões,
  pessoas identificadas nem decisões judiciais. Não equiparar o município
  retornado ao município do órgão julgador do DataJud sem validação geográfica.

## Fontes que exigem participação do pesquisador
- Dados individuais do INSS/CadÚnico ou inteiro teor em lote no PJe exigem
  autorização institucional e revisão da governança de dados. Não presumir que
  o caráter público de um processo autoriza extração irrestrita de seus dados.

## Reavaliação: documentos públicos e códigos — 06/10/2026

### O que pode melhorar a qualidade

| Fonte | Conteúdo confirmado | Acesso e limite observado |
| --- | --- | --- |
| [Jurisprudência TRF1/JEF — CJF](https://jurisprudencia.cjf.jus.br/trf1/index.xhtml) | Pesquisa de acórdãos, decisões monocráticas, súmulas e arguições, com fontes TRF1/JEF1. | Página pública acessível; [carta de serviços TRF1](https://www.trf1.jus.br/trf1/carta-servicos/jurisprudencia) informa consulta livre. Não foi comprovada API documentada de coleta em lote nem cobertura de processos da amostra. |
| [Arquivo de inteiro teor TRF1](https://arquivo.trf1.jus.br/) | Busca por número de processo de documentos publicados; o portal informa DOC e TIFF. | Formulário público confirmado, não autos completos. Disponibilidade de documento para cada CNJ da amostra ainda não medida. A [FAQ TRF1](https://www.trf1.jus.br/trf1/ouvidoria/perguntas-frequentes) descreve inteiro teor de processos físicos. |
| [STJ — espelhos de acórdãos](https://dadosabertos.web.stj.jus.br/group/jurisprudencia) | Catálogo de jurisprudência em CSV/JSON/ZIP; espelhos, não garantia de íntegra de autos. | `GET https://dadosabertos.web.stj.jus.br/api/3/action/package_search?q=jurisprudencia&rows=1` testado sem credencial. Importador existente filtrou por menção explícita a BPC/LOAS; um lote foi interrompido após salvar 1 documento (coleta marcada como falha parcial). |
| [INSS — indeferimentos](https://dadosabertos.inss.gov.br/dataset/beneficios-indeferidos-plano-de-dados-abertos-jun-2023-a-jun-2025) | Competência, espécie, motivo de indeferimento, UF e outros campos administrativos. | Recursos públicos mensais; contexto de negativas administrativas, não ligação comprovada com ações judiciais. Não atribuir motivo agregado a uma pessoa/processo. |

O [dataset Segunda Turma do STJ](https://dadosabertos.web.stj.jus.br/dataset/espelhos-de-acordaos-segunda-turma)
descreve seleção técnico-documentária de acórdãos, histórico inicial e atualizações,
com possível repetição de IDs entre arquivos. Um importador precisa deduplicar por
ID e preservar origem, data e corpus. Não misturar a seleção recursal STJ com
a população de concessões iniciais TRF1/DF nem calcular taxa de procedência
do recorte com esses julgados.

**Prioridade proposta:** piloto separado de documentos TRF1/JEF; STJ como corpus
complementar para fundamentos e construção de categorias; INSS para contexto.
Termos de pesquisa: `"benefício assistencial"`, `"benefício de prestação continuada"`,
`BPC`, `LOAS`, `"art. 203"`. Pesquisar número CNJ quando disponível, sem presumir
que um acórdão de tribunal superior corresponda automaticamente ao CNJ de origem.
Respeitar limites de acesso; não contornar CAPTCHA ou anti-robô. Nenhuma dessas
novas fontes de documentos foi integrada à triagem nesta atualização.

### Códigos de assunto

A TPU local em `datajud/datajud/tb_CNJ/OUTPUT/Assuntos/assuntos_JF1G.csv` mantém
`6114` (Benefício Assistencial) e filhos `11946` (Pessoa com Deficiência) e
`11947` (Idoso). Não foi identificado no snapshot outro filho direto de 6114.
O [CNJ — Justiça em Números 2023](https://bibliotecadigital.cnj.jus.br/bitstream/123456789/727/1/justica_em_numeros_2023_010923__1_.pdf)
também apresenta esses códigos e o vínculo entre benefício assistencial e seus
subassuntos. A consulta on-line SGT retornou 403 nesta verificação; não afirmar
que o snapshot local é a versão mais recente da tabela.

`6117` — Renda Mensal Vitalícia aparece no catálogo e em
[consulta pública TRF1](https://processual.trf1.jus.br/consultaProcessual/processo.php?proc=00000029220194019197&secao=TRF1).
É candidato a estudo complementar, não substituto nem ampliação automática do
recorte BPC. Assuntos amplos de revisões, renda inicial ou assistência misturam
benefícios e pedidos fora do escopo. Os comandos continuam limitados aos três
códigos originais; ampliar a amostra por período/tribunal requer explicitar a
mudança de população, em vez de acrescentar códigos genéricos indiscriminadamente.

### Decisão para o processamento atual

Não declarar ausência de texto público: há portais de decisões e uma base STJ
em formato aberto. Tampouco prometer acesso em lote a petições e sentenças do
nosso recorte. Até testar/importar documentos com vínculo e origem, a triagem
permanece DataJud + TPU, agora com resumo natural, e não identifica motivo da
judicialização ou resultado individual. Ver contrato v1.2 em `CONTRATOS.md` e
comando de lote em `SEM_DOCKER.md`.

## Implementação e evidência de coleta — 06/10/2026

- **CJF/TRF1/JEF1:** formulário público JSF (`formulario:textoLivre`,
  `formulario:selectTiposDocumento`, checkbox da base e ViewState), cookies de
  sessão e paginação AJAX. Acórdãos/decisões publicados ficam em
  `documentos_publicos`, com ID da origem, campos, texto, hashes e Bronze HTML/XML.
  Piloto persistiu 5 TRF1 e 5 JEF1. Duas páginas JEF1 retornaram 30 + 30 IDs sem
  sobreposição. HTTP 504 ocorreu em uma consulta mais pesada e ficou como erro,
  não ausência de dados. Nenhum documento foi vinculado por similaridade.
- **STJ:** download de recursos JSON recentes selecionados pelo CKAN, filtrados
  por termos explícitos BPC/LOAS/benefício assistencial; ID da origem e conteúdo
  são versionados. JSON agosto/2026 da Segunda Turma retornou 1 candidato, gravado;
  repetir gravou zero versões novas. O número curto `3126923` não foi convertido
  nem unido a CNJ. A opção `--historico` agora inclui ZIP oficial antes dos
  recursos recentes, preservando seus bytes e lendo membros JSON sem extração
  no disco. O ZIP histórico real da Segunda Turma tem 95.529.644 bytes e cinco
  JSONs (413.639.349 bytes expandidos), até maio/2022. Limites: 128 MiB de
  download/por membro e 1 GiB expandido total. Limitar a coleta não demonstra
  cobertura completa, e repetir o mesmo limite não avança um checkpoint.
  A execução real com `--historico --limit 20` terminou como `concluida` e
  gravou 20 versões novas. Corpus local: 21 STJ + 10 CJF; a amostra permanece
  com 2.584 processos e zero vínculos documentais.
- **INSS:** recurso oficial de agosto/2026 (XLSX, 63.610.786 bytes) lido integralmente
  em modo streaming. Título/cabeçalho e par de colunas espécie código/descrição
  foram tratados pelo layout observado. 882.589 linhas lidas; DF: 3.258 espécie 87,
  389 espécie 88, em 24 grupos de motivo. Só agregados são gravados na Silver.
  XLS histórico ainda requer importador próprio. O novo comando
  `inss-concessoes` usa o [dataset oficial de concessões](https://dadosabertos.inss.gov.br/dataset/beneficios-concedidos-plano-de-dados-abertos-jun-2023-a-jun-2025),
  valida código/descrição de despacho e espécie e competência em todas as
  linhas. Arquivo agosto/2026: 125.588.346 bytes, 848.996 linhas lidas; DF:
  1.495 concessões espécie 87 e 667 espécie 88, em 8 agregados, efetivamente
  gravados em `indicadores_inss_concessoes`. A API retornou HTTP 200 e os mesmos
  totais. Despacho 4 é rotulado pela fonte `Concessao Decorrente de Acao Judicial`;
  a descrição é preservada, sem atribuição a um processo ou cálculo de
  procedência judicial. Nenhum CID, nascimento ou linha individual foi persistido
  na Silver. Migração aditiva 0007 para PostgreSQL; SQLite cria somente a tabela.
- **Arquivo TRF1:** acesso variou entre Cloudflare e formulário acessível. O endpoint
  público usado pelo próprio script `js/pages/index.js` foi testado:
  `POST /localiza_processo.php`, campo `ProcInclui` com CNJ sem pontuação. Sem
  credencial. CNJs testados (2022, 2009, 2013) retornaram `existeProcesso:false`.
  CLI `arquivo-trf1 --baixar` agora guarda a listagem e baixa DOC/TIFF a partir
  dos links publicados. Controle positivo de outro tema: CNJ
  0058364-48.2010.4.01.0000, citado na publicação oficial
  [Sequestro Internacional Parental](https://www.trf1.jus.br/trf1/conteudo/files/Sequestrointernacionalparental.pdf).
  Um BPC da própria base, 0003970-58.2006.4.01.4001 (Piauí, fora DF/RIDE),
  também foi localizado: certidão em texto simples e ementa DOC binária foram
  baixadas e vinculadas. São os primeiros dois vínculos reais dessa fonte.
  A conversão preliminar de DOC binário agora usa `legacy-doc` 0.2.1 em Python,
  sem Word/macros/rede; não garante formatação ou conteúdo integral. Recuperou
  3.217 caracteres da ementa BPC e 5.614 da decisão de controle, criando outras
  versões, sem sobrescrever originais nem transmitir dados à IA. Hash do
  original, parser, versão e hash do texto ficam registrados. TIFF/OCR permanece
  pendente; certidão com cabeçalho
  conhecido e extensão DOC, mas bytes de texto simples, foi decodificada sem OCR.
  A API/painel distingue `extracao_texto=pendente` de `texto_simples`.
  Não houve bypass,
  envio de e-mail automático ou uso de credencial institucional.
- **MCP DeHor:** o [README atual](https://github.com/DeHor-Labs/mcp-juridico-brasil)
  descreve DataJud e ferramentas de monitoramento/prazos, não nova base de inteiro
  teor. Não foi instalado: reutilizar o que já temos não resolve cobertura textual.

O comando `cjf-amostra` consulta candidatos BPC públicos TRF1/G1/JE de órgãos
de Brasília usando os números da base, sem pontuação. O portal rejeita hífen
na pesquisa livre. Teste de controle com número de documento já conhecido
retornou um documento; consultas reais de 10 candidatos no TRF1 e 5 no JEF1
retornaram zero. Esses vazios ficam em `coletas` e a próxima execução avança
na mesma base/configuração; erros/bloqueios não viram vazio. Isso não comprova
inexistência de documentos no processo. O comando não depende da triagem IA.

O pacote SQLite no Git permanece o original; os dados novos estão só em
`data/bpc-remote.sqlite` local e são reproduzíveis pelos comandos de coleta no
ambiente remoto. Não enviar os textos/microdados brutos ao Git nem à API IA
automaticamente. O painel `/admin/documentos` exibe corpus e agregados separados.

## Pesquisa adicional: TNU, TRF3 e TRF5 — 06/10/2026

Foram lidas páginas oficiais com texto decisório público, sem fornecer
credencial. Isso confirma exemplos acessíveis, não uma API documentada,
permissão de coleta irrestrita ou cobertura integral. Nesta rodada não houve
importação desses documentos nem alteração da população ou do schema.

| Fonte | Exemplo real e utilidade | Situação |
| --- | --- | --- |
| [TNU — inteiro teor](https://eproctnu-jur.cjf.jus.br/eproc/externo_controlador.php?acao=jurisprudencia%40jurisprudencia%2Fdownload_inteiro_teor&id_jurisprudencia=771782816310867611465715976907) | CNJ `5006875-14.2022.4.04.7005`, Paraná: relatório e voto sobre BPC, autismo e avaliação biopsicossocial. O texto descreve pedido e decisões nas instâncias anteriores. | Prioridade para corpus textual complementar; não integrado. Não equivale aos autos completos nem representa DF/RIDE. |
| [TRF3 — documento publicado](https://web.trf3.jus.br/acordaos/Acordao/BuscarDocumentoPje/344467700) | CNJ `5000929-32.2025.4.03.6343`, São Paulo: relatório e voto sobre concessão de BPC; relato de negativa administrativa pelo critério econômico e discussão de renda/despesas. | HTML público confirmado; não integrado. O endereço recebe ID de documento, não número CNJ: não inventar IDs nem links. |
| [TRF5 — jurisprudência](https://jurisprudencia.trf5.jus.br/jurisprudencia/exibir.wsp?tmp.id_documento=165824) | Texto público sobre benefício assistencial e CadÚnico. | Exemplo acessível; não integrado. A busca, paginação, estabilidade e cobertura ainda exigem piloto próprio. |

O [repositório oficial TNU](https://www.cjf.jus.br/cjf/corregedoria-da-justica-federal/turma-nacional-de-uniformizacao/publicacoes-1/repositorio-tnu/repositorio-tnu/@@download/arquivo)
também oferece PDF com CNJs, ementas e teses. A versão aberta nesta rodada
informa atualização em 22/06/2026. É índice de jurisprudência selecionada,
útil para localizar casos e construir categorias, não amostra aleatória.

Decisão: há como melhorar o conteúdo; priorizar um piloto TNU e documentos
publicados das turmas recursais, mantendo-os separados da população original.
Antes de alimentar a IA com esses textos, definir contrato próprio de evidências
documentais, anonimização, estágio da decisão e revisão humana. O piloto atual
`ipeaia-triagem` continua enviando somente metadados DataJud + TPU e salvando
`resumo_caso` em português simples dentro de `extracoes_ia.resultado` (v1.2).
Não atribuir aos casos atuais motivos encontrados em outros julgados.

### Integração do piloto HTML

O novo comando `documentos-publicados --urls <links oficiais>` usa somente
rotas verificadas TNU/TRF3/TRF5, guarda HTML original antes da interpretação e
persiste no corpus versionado existente. Não descobre links por enumeração de
IDs. Na página TNU acima, a resposta real contém sete artigos: seis têm termos
BPC e foram gravados separadamente com seus IDs explícitos (relatório/voto,
voto-vista, voto divergente, ementa/acórdão e dois extratos de ata). Isso não
significa seis processos: todos identificam o mesmo CNJ. Um artigo sem termo
temático não foi selecionado. O documento TRF5 foi gravado com CNJ explícito
`0504973-21.2019.4.05.8108` e 14.684 caracteres de texto publicado.

Reexecução real das duas URLs produziu zero versões novas. API local retornou
HTTP 200, seis documentos TNU e um TRF5; os processos permaneceram 2.584.
Os sete documentos não criaram vínculos novos com a amostra. O painel permite
filtrar pelas novas fontes. Chamadas diretas TRF3 tiveram timeout nesta rodada,
apesar do documento acessível na pesquisa web: não confundir com ausência de
texto nem alegar coleta TRF3 concluída. Busca automática de outros links,
cobertura integral e validação humana dos textos seguem pendentes.

### Descoberta e lote retomável TNU

`tnu-pesquisa --query LOAS --limit 10 --paginas 5` agora busca links diretamente
no formulário público e consulta os pendentes. A origem TNU vem da opção do
HTML, sem valor numérico presumido. POST `listar_resultados` com pesquisa em
inteiro teor e agrupamento; AJAX `ajax_paginar_resultado` com
`hdnPaginaAtual`, nos mesmos cookies e controles públicos. Sem credencial.
Preserva HTML inicial/pesquisa/AJAX antes de interpretar, valida contagens,
IDs e links; não enumera IDs nem segue rotas autenticadas.

Evidência real: LOAS informou 534 resultados e 54 páginas de 10 itens.
Duas páginas retornaram 20 links diferentes. Isso é volume informado pelo
portal, não 534 documentos baixados nem processos da amostra. Primeiro lote
de três URLs acrescentou seis documentos; repetir com limite dois pulou as
três URLs concluídas e acrescentou dois documentos de outras duas URLs.
API TNU retornou HTTP 200, 14 documentos com texto e seis CNJs distintos no
primeiro lote; depois, a busca "benefício de prestação continuada" percorreu
duas páginas, consultou 10 URLs novas e acrescentou 16 documentos, elevando o
corpus TNU a 30 documentos e 16 CNJs distintos.
incluindo o controle anterior. Corpus total local: 85 versões; população
DataJud: 2.584; vínculos: os mesmos três de um único caso do Piauí.

O limite conta URLs, não artigos/processos. Repetir examina pendentes nas
páginas solicitadas; ampliar páginas permite examinar outros resultados.
`--retentar` reconsulta também URLs já concluídas. Ordenação e agrupamento
ficam no manifesto; mudanças entre execuções impedem alegar completude.
O texto continua local e não entra automaticamente na triagem IpeaIA.
Controle negativo real com termo inexistente retornou o título
`0 documentos encontrados`, mas omitiu os valores dos campos de totais.
O parser só reconhece esse vazio com título/área/metadados únicos e página 1
confirmada, sem cards. O CLI terminou `sem_resultado`, conservando a resposta
original; ausência genérica de valores ou HTML de erro continua sendo falha.
Teste direto TRF3 com curl IPv4 também terminou em timeout sem bytes;
o link público TRF5 de navegação `login/acesso.wsp` redirecionou para HTTP 404.
Não contornar acesso: TRF5 permanece disponível por links publicados,
A busca automática ainda estava pendente quando essa primeira avaliação foi registrada.

### Pesquisa pública TRF5 confirmada

O formulário público em
[pesquisa.wsp](https://jurisprudencia.trf5.jus.br/jurisprudencia/pesquisa.wsp)
funcionou sem credencial, mantendo cookies de sessão. A pesquisa simples
envia `POST /jurisprudencia/resultado_pesquisa.wsp` com `tmp.search.query`,
complemento vazio, `tmp.ds_legislacao_2` vazio, quantidade 10 e
`tmp.search.acao=novapesquisa`, conforme o formulário e seu JavaScript.
LOAS informou 2.233 resultados nesta consulta. Esse total não indica cobertura
DF/RIDE nem documentos importados. O comando `trf5-pesquisa --query LOAS
--limit 10 --paginas 2` automatiza busca e paginação com retomada. Preserva
respostas e usa IDs publicados nos resultados; valida offsets, totais, contagem
por página e duplicatas. URLs já concluídas são puladas; `--retentar` força nova
consulta. O lote percorreu duas páginas e importou 10 documentos. A busca
`benefício assistencial` também retornou documentos. Os 2.233 resultados
informados são volume da busca LOAS, não medida de relevância BPC, recorte
geográfico ou cobertura completa.

Três links de documentos efetivamente publicados foram importados pelo comando
existente, com IDs 4036, 3843 e 5036. O parser agora preserva o formato pré-CNJ
observado, sem convertê-lo nem criar vínculo. A busca paginada adicionou mais
11 documentos, e a busca com termo acentuado acrescentou um. Total local: 85
versões de documentos, 30 TNU e 16 TRF5; os 2.584 processos e três vínculos
foram preservados.
SQLite passou na verificação de integridade e não apresentou violações de
chaves estrangeiras. Dados coletados permanecem locais, não no Git e não
enviados automaticamente à IpeaIA. Uma seção Ementa pode estar vazia na fonte;
não preencher com texto de outra seção nem afirmar disponibilidade de autos.

### TRF3: serviço público confirmado, coleta direta indisponível

A [Carta de Serviços do TRF3](https://www.trf3.jus.br/carta-servicos/acordaos)
confirma consulta pública do inteiro teor (relatório, voto e ementa) por número
do processo. A página de [instruções](https://web.trf3.jus.br/acordaos/Acordao/Instrucoes)
orienta consultar o andamento, pesquisar o CNJ, abrir a data de disponibilização
e contatar a DEDI se o serviço estiver indisponível. Não descreve API pública
em lote nem busca temática. Em 06/10/2026, o status oficial indicava os serviços
operacionais, mas três URLs de consulta/documento expiraram por timeout neste
ambiente. Resultado: fonte pública existe, integração automática viável não foi
confirmada; não gravamos documento TRF3 nem classificamos timeout como vazio.

### DataJud TRF1: expansão exploratória para RIDE-DF (07/10/2026)

A [lista oficial da Sudeco](https://www.gov.br/sudeco/pt-br/assuntos/ride-df)
inclui Formosa e Luziânia entre os municípios da RIDE-DF. Como ambos aparecem
na amostra sob os nomes de órgão "Vara Única de Formosa" e "Vara Única de
Luziânia", consultamos TRF1, graus G1/JE e assuntos 6114/11946/11947 com
`datajud --municipio-codigos 1798 2788`. A busca percorreu com `search_after`
três lotes de 500 hits e retomou um lote interrompido de 450 hits, chegando a
1.950 hits registrados em `coletas`. Na cópia SQLite local, Formosa tem 1.024
processos e Luziânia 926; o universo cresceu de 2.584 para 4.531 processos
(+1.947 líquidos, pois há sobreposições). O volume coletado não representa
todos os municípios nem todos os processos da RIDE.

Importante: o [glossário DataJud](https://datajud-wiki.cnj.jus.br/api-publica/glossario/)
descreve `orgaoJulgador.codigoMunicipioIBGE` como código municipal IBGE; os
valores crus observados neste TRF1 foram 743, 1798 e 2788 (não códigos IBGE de
sete dígitos). Portanto, não os geocodificamos como IBGE. Nesta busca, a
identificação de Formosa/Luziânia usou conjuntamente o valor cru e o nome do
órgão, conferido com a lista Sudeco. A cobertura dos demais 31 municípios e o
motivo pelo qual a API diverge do glossário continuam pendentes de validação.

Esta inclusão amplia somente a população DataJud: não houve novos documentos
ou vínculos processuais. O corpus permanece com 85 versões (11 CJF, 21 STJ,
7 arquivo TRF1, 30 TNU e 16 TRF5), das quais três versões estão ligadas a um
processo do Piauí. Integridade SQLite: `ok`; violações de chave estrangeira: 0.

### Complemento territorial por jurisdição e TRF6 (07/10/2026)

A [Resolução Presi TRF1 13/2026 e seu anexo](https://www.trf1.jus.br/sjgo/noticias/trf1-publica-resolucao-que-consolida-a-jurisdicao-das-secoes-e-subsecoes-judiciarias-da-1a-regiao)
confirmam, para GO, municípios da RIDE nas jurisdições de Anápolis, Formosa,
Luziânia, Goiânia e Uruaçu. A jurisdição oficial de [Unaí no TRF6](https://sjmg.trf6.jus.br/jurisdicoes/)
inclui Arinos, Buritis, Cabeceira Grande e Unaí, os quatro municípios mineiros
da RIDE segundo a [Sudeco](https://www.gov.br/sudeco/pt-br/assuntos/ride-df).
Assim, a cobertura pela região do tribunal não é equivalente a TRF1 apenas.

Consultas DataJud públicas por `assuntos.codigo` 6114/11946/11947 e graus
G1/JE localizaram estes códigos crus de órgão: TRF1 Brasília 743, Formosa
1798, Luziânia 2788, Anápolis 216, Uruaçu 5332 e Goiânia 1903; TRF6 Unaí
3170404. Os totais da API na consulta foram, respectivamente, 49.231, 6.300,
8.253, 12.833, 4.618, 46.025 e 4.314 hits. O banco recebeu novos lotes de
1.000 hits por código TRF1 e os 4.314 hits TRF6 de Unaí (10.314 hits novos);
processos passaram de 4.531 para 11.865 (+7.334 líquidos), com 11.922 registros.
Totais de API e hits de coleta não são processos únicos: há duplicatas entre
assuntos, graus, atualizações e coletas.

Este é um pool de candidatos por sede do órgão, não um recorte verificado por
residência. Anápolis, Goiânia e Uruaçu ficam fora da RIDE, embora suas
jurisdições alcancem municípios nela; os casos dessas sedes permanecem
suplementares e não devem ser rotulados como residentes da RIDE sem evidência
processual. Unaí é sede em município da RIDE, mas sua jurisdição também abrange
localidades fora dela. O TRF6 é uma ampliação do universo jurisdicional em
relação ao plano TRF1, e deve ficar identificada separadamente nas análises.

No TRF1, os valores crus continuam divergindo do formato IBGE de sete dígitos
descrito pelo [glossário DataJud](https://datajud-wiki.cnj.jus.br/api-publica/glossario/);
no TRF6, o retorno de Unaí (3170404) coincide com o código IBGE oficial. Não
normalizar os valores TRF1 como IBGE. O parser passou a achatar listas aninhadas
de `assuntos` preservando `codigo` sem nome como `nome: null`, enquanto Bronze
e payload JSON mantêm o original. Teste observado em Goiânia: `[[{"codigo":
11946,"nome":"Deficiente"}],{"codigo":15516}]`. 99 testes passaram com
`DATABASE_URL=sqlite:///:memory:`; a conexão PostgreSQL do ambiente Windows não
carrega `libpq`, portanto esse teste não valida PostgreSQL.

### TRF6: inteiro teor publicado e TJMG por sede (07/10/2026)

O [portal público de jurisprudência eproc do TRF6](https://eproc2g.trf6.jus.br/eproc/)
tem busca textual aberta; o [manual oficial](https://eproc-jur.trf6.jus.br/eproc/modulos/jurisprudencia/ajuda/doc/Manual_Jurisprud%C3%AAncia.pdf)
descreve pesquisa em inteiro teor, filtros e apresentação do documento completo.
Não encontrei API REST documentada. Validei o formulário e a paginação AJAX e
implementei `trf6-pesquisa`: BPC informou 4.134 resultados na origem TRF6,
19 na TRU6 e 6.566 nas Turmas Recursais; Varas Federais retornaram zero em
consultas BPC e LOAS. Foram coletadas 10 decisões da origem TRF6, cinco da
TRU6 e cinco das Turmas Recursais: 20 versões TRF6 no corpus e 105 documentos
públicos no total. O texto pode conter dados pessoais; permanece
local, não foi exibido como dado de usuário nem enviado à IpeaIA. Revisão de
privacidade é necessária antes de divulgação ou processamento externo. Total
do portal não significa processos únicos nem casos do recorte DF/RIDE.

Cada card da busca oferece um CNJ próprio; o coletor compara esse número ao
documento e não confunde processos citados no voto com o caso julgado. Busca BPC
foi validada em duas páginas de dez; o lote retomável consultou cinco URLs,
pulou quatro já completas e importou cinco novas. A primeira tentativa falhou
diante de citações múltiplas e foi recuperada com a validação pelo CNJ do card.
CLI: `python -m bpc_ingestion trf6-pesquisa --query BPC --limit 10 --paginas 5`.
O padrão pesquisa a origem TRF6; `--origens` também aceita valores rotulados
TRU6 e Turmas Recursais foram testadas em lote; Varas Federais tiveram zero
resultados nos termos testados. Os resultados das origens suplementares não
devem ser atribuídos a DF/RIDE sem confirmação pelo município/órgão do caso.

Consulta pública DataJud ao TJMG, com os mesmos assuntos, grau G1 e códigos
IBGE de Arinos (3104502), Buritis (3109303), Cabeceira Grande (3109451) e Unaí
(3170404), encontrou e persistiu 361 registros: 274 Arinos, 52 Buritis, 35
Unaí e nenhum Cabeceira Grande. Podem incluir competência federal delegada,
mas isso não foi validado registro a registro. Tratar como pool suplementar,
sem misturar ao universo TRF1/TRF6 e sem presumir residência pelo órgão.

O lote do Comunica PJe consultou 100 processos e acrescentou 13 comunicações;
há 55 no total. São comunicações/intimações, não inteiro teor nem petições.
Erros HTTP 500 transitórios foram repetidos pelo coletor e terminaram em 200;
`sem_resultado` segue distinto de erro. A cópia local agora tem 12.224
processos, 12.283 registros DataJud, três vínculos documento-processo e passou
`PRAGMA integrity_check` (`ok`) sem violações de chaves estrangeiras.

### Fontes restantes e restrições (07/10/2026)

### TRF2: jurisprudência e inteiro teor público (07/10/2026)

O [portal de jurisprudência da 2ª Região](https://jurisprudencia-eproc.trf2.jus.br/)
é indicado pelo [TRF2](https://www.trf2.jus.br/jf2/noticia-jf2/2024/justica-federal-da-2a-regiao-tem-novo-portal-de-jurisprudencia)
e cobre decisões de 1º e 2º graus e Turmas Recursais. O formulário eproc novo
está em `https://eproc.trf2.jus.br/eproc/externo_controlador.php` e permite
pesquisa aberta por texto nas origens TRF2, TRU2 e Turmas Recursais. Não encontrei
API REST documentada; integrei o POST/AJAX público em `trf2-pesquisa`. A busca
`BPC` reportou 5.927 hits TRF2, 29 TRU2 e 16.367 Turmas Recursais; foram
coletadas 10 decisões TRF2, cinco TRU2 e cinco das Turmas Recursais (20 versões).
Cada CNJ é validado no link de consulta do card e novamente no cabeçalho do inteiro teor para impedir
vínculo por citação. A origem não amplia a amostra TRF1/DF-RIDE. Textos locais,
sem envio à IpeaIA, e retidos da API administrativa até revisão de privacidade.

Os 20 documentos foram persistidos no PostgreSQL configurado para a ingestão,
junto com os 20 documentos TRF4; não criam processos ou vínculos automáticos.
`data/bpc-remote.sqlite` não foi sincronizado nesta rodada.

### TRF4: jurisprudência e inteiro teor público (07/10/2026)

O [portal oficial de jurisprudência TRF4](https://jurisprudencia.trf4.jus.br/eproc2trf4/externo_controlador.php?acao=jurisprudencia%40jurisprudencia%2Fpesquisar)
permite busca livre em inteiro teor, com origens TRF4, TRU4 e Turmas Recursais,
conforme o [manual oficial](https://eproc-jur.trf4.jus.br/eproc2trf4/modulos/jurisprudencia/ajuda/doc/Manual_Jurisprud%C3%AAncia_TRF4.pdf).
Não encontrei API REST documentada; a busca web POST/AJAX foi validada e integrada
em `trf4-pesquisa`, que só segue links oficiais `download_inteiro_teor`, confere
o CNJ do card com o parâmetro do link público e valida novamente esse CNJ no
cabeçalho do documento (não em citações ao longo do voto). A consulta `BPC`
reportou 6.917 resultados TRF4, 443 TRU4 e 25.342 Turmas Recursais nesta
execução. Foram coletadas 10 decisões TRF4, cinco TRU4 e cinco das Turmas
Recursais (20 versões), sem processo ou vínculo automático. O número reportado
é total de hits, não de processos únicos. TRF4 é corpus suplementar, fora do
recorte TRF1/DF-RIDE.
Os textos podem conter dados pessoais: permanecem locais, ocultos na API do
painel até revisão de privacidade e não são enviados à IpeaIA.
Os 20 documentos ficaram na instância PostgreSQL configurada para a ingestão;
ela contém 2.584 processos e 2.588 registros DataJud. A cópia SQLite
`data/bpc-remote.sqlite` usada no ambiente remoto não foi atualizada nesta
coleta e exige transferência separada.

### DataJud TJGO: varredura suplementar da RIDE-GO (07/10/2026)

A [Sudeco](https://www.gov.br/sudeco/pt-br/assuntos/ride-df) enumera 29 municípios
goianos da RIDE; seus geocódigos foram obtidos no [serviço oficial de localidades
do IBGE](https://servicodados.ibge.gov.br/api/docs/localidades). Pré-consulta e
coleta DataJud em `api_publica_tjgo` filtraram assuntos 6114/11946/11947,
`grau` G1/JE e `orgaoJulgador.codigoMunicipioIBGE` pelos 29 códigos. O DataJud
informou e a coleta gravou 4.513 hits (4.513 CNJs distintos observados), com
`source-mode essencial`; a base PostgreSQL passou a 7.097 processos e 7.101
registros DataJud. São processos em órgãos estaduais localizados nesses
municípios, não prova de residência do requerente nem de que cada ação use
competência federal delegada. Permanecem separados do universo principal
TRF1/DF-RIDE. A cópia SQLite do ambiente remoto não foi sincronizada.

O lote usa os mesmos códigos de assunto DataJud; contagens de hits não devem ser
somadas às de outras consultas sem deduplicação por CNJ/registro. A filtragem
geográfica é pelo órgão julgador, não pelo domicílio da parte.

O [Arquivo de inteiro teor do TRF1](https://arquivo.trf1.jus.br/) respondeu sem
credencial; a coleta existente já lê links de documentos publicados. O teste
`verificar-arquivo-trf1` preservou a página inicial. Em seguida, cinco CNJs
TRF1 do pool DataJud foram consultados sem baixar documentos; a API respondeu
`sem_resultado` para esse lote. Isso não prova inexistência de documentos nos
autos nem ausência de outros julgados publicados. O portal não documenta uma API
de lote para petições iniciais ou
autos completos. Consulta processual pública não deve ser confundida com
autorização de acesso ao processo eletrônico integral; qualquer CAPTCHA ou
credencial institucional encerra a automação, sem contorno.

Repeti uma vez o GET direto do exemplo público TRF3 já pesquisado
(`BuscarDocumentoPje/344467700`); terminou em `TimeoutError` sem resposta. Não
há nova importação TRF3, e não vou tentar contornar esse bloqueio de transporte.
A [API pública do Portal TRF1](https://www.trf1.jus.br/trf1/api-noticias-institucionais)
trata de notícias institucionais, não de processos ou decisões; portanto não é
fonte de caso para este objetivo.

O [Portal da Transparência da CGU](https://portaldatransparencia.gov.br/api-de-dados)
tem endpoint BPC por município, mas a extração agregada já é tratada em
`transparencia-bpc` e não deve ser duplicada como casos judiciais. Sua consulta
por CPF/NIS é deliberadamente excluída. O plano de pesquisa `plano.txt` determina
tratamento local de dados pessoais e divulgação só agregada/anonimizada; por
isso documentos judiciais capturados não são enviados à IpeaIA nem a outro
serviço externo até aprovação ética e revisão de privacidade. As decisões
publicadas continuam sendo material não confiável para análise, não evidência
automática de perfil ou resultado.

### Verificação adicional TRF3, TJMG e STJ (07/10/2026)

No TRF3, tanto a página pública de pesquisa `https://web.trf3.jus.br/jurisprudencia/home/index/1`
quanto a consulta direta de documento publicada já avaliada expiraram por timeout
(90 segundos na página de pesquisa). O site oficial documenta consulta de acórdãos
por número CNJ e disponibilidade do inteiro teor, mas não foi possível testar
busca/coleta estável nesta execução. Sem implementação nova nem documentos TRF3
gravados; não contornar o bloqueio de transporte.

O formulário oficial do [TJMG](https://www5.tjmg.jus.br/jurisprudencia/formEspelhoAcordao.do)
respondeu, mas o POST de pesquisa retornou HTTP 401 com página “Informe o código”,
indicando CAPTCHA. A ajuda oficial confirma pesquisa pública de acórdãos por
ementa/inteiro teor, mas a automação foi encerrada sem contornar o CAPTCHA.
Além disso, acórdãos estaduais não são equivalentes à população de ações federais
de BPC; só seriam um corpus comparativo separado, após consulta humana e
validação de relevância.

O importador oficial STJ já existente foi testado com os conjuntos de espelhos
das Turmas. Um documento que menciona BPC/LOAS foi persistido no PostgreSQL; a
execução foi interrompida por demora ao processar o próximo recurso e a coleta
ficou marcada como `falhou`, com `registros=1`. Não é lote completo nem estimativa
de cobertura. O documento permanece no corpus separado `fonte=stj`, sem processo
ou vínculo presumido e sem envio à IpeaIA. A demora foi reavaliada no piloto
Luna: `curl` e Python consultaram o mesmo recurso público de 1.410.751 bytes;
ambos receberam HTTP 206 para faixa de 1.024 bytes em menos de 1,1 s, e Python
leu o JSON integral (338 registros) em 0,369 s. Uma consulta posterior limitada
a um recurso/um documento concluiu sem inserir nova versão porque o registro
já existia. A demora anterior não se reproduziu; não houve novo lote grande.

### Execução Luna: cobertura documental até 200 casos e fontes suplementares (07/10/2026)

O manifesto reproduzível com seed `20261007` selecionou 200 CNJs: 100 do núcleo
TRF1 com município do órgão DataJud 743 (DF), 50 de Formosa e 50 de Luziânia.
As duas últimas sedes são candidatas suplementares da RIDE; o município do
órgão julgador não comprova domicílio da parte. A base de candidatos tinha
3.823 CNJs. A seleção inclui assuntos 6114 e descendentes TPU 11946/11947.

As 200 buscas explícitas ao CJF/JEF1 tiveram 204 tentativas devido a quatro
repetições, 200 CNJs únicos e um acórdão com CNJ exato. Houve 199 casos únicos
sem resultado e zero falhas/bloqueios. O [serviço público CJF/TRF1](https://jurisprudencia.cjf.jus.br/)
é fonte de julgados/espelhos e não de autos integrais. O [Arquivo de inteiro
teor do TRF1](https://arquivo.trf1.jus.br/) não encontrou documento para os 200
CNJs; cada resposta original foi preservada. Sem resultado nessa busca não
significa ausência de peças nos autos.

O [Comunica PJe](https://comunicaapi.pje.jus.br/) retornou 56 comunicações em
35/200 casos; os outros 165 não tiveram publicação encontrada. Houve 29
respostas HTTP 500 transitórias repetidas até HTTP 200 e nenhum erro final. As
classificações de tipo documental incluem 9 casos com `Sentença Tipo C`, 2 com
`Decisão` e 3 com `Acórdão` (13 casos distintos, com sobreposição). Um ato
classificado como decisão é incidental, em habilitação de herdeiros/RPV durante
cumprimento de sentença. Em revisão local de dez documentos positivos, três
sentenças Tipo C encerram mandados de segurança sem resolução do mérito e um
acórdão informa desfecho recursal. Motivo administrativo explícito de
indeferimento: 0/200. Esses números são cobertura de publicação, não taxa de
procedência ou medida da disponibilidade de autos.

O grupo DF teve publicação em 18/100 casos, Formosa 7/50 e Luziânia 10/50.
Em 2026, 12/14 casos tiveram comunicação, contra 7/16 em 2025 e 4/11 em 2024;
de 2018 a 2023 houve 3/123. A diferença acompanha idade/recência de publicação
e não deve ser interpretada como diferença de mérito. A página oficial do
[eDJF1 por cadernos](https://www.trf1.jus.br/sjgo/diarios-oficiais/diario-eletronico-da-justica-federal-da-1-regiao-edjf1)
foi examinada; o caderno GO de 14/02/2022 estava disponível em PDF, mas informava
que não havia atos judiciais a divulgar. Não se associou processo a uma edição
sem trecho/cabeçalho verificável.

Para o corpus complementar, foram consultadas cinco URLs por fonte (TNU,
TRF2, TRF4, TRF5 e TRF6), 25 URLs ao todo, produzindo 21 versões novas. Os
resultados continuam separados de amostra de concessão inicial DF/RIDE e não
foram ligados por citação de precedente.

### INSS agregado: junho–agosto de 2026 (07/10/2026)

O catálogo oficial do [INSS Dados Abertos](https://dadosabertos.inss.gov.br/)
oferecia três competências contínuas recentes para concessões e indeferimentos.
Os seis XLSX foram baixados uma vez cada e processados para DF, GO e MG, com os
agregadores existentes. Quantidades agregadas por competência/UF:

| Competência | Indeferimentos DF/GO/MG | Concessões DF/GO/MG |
|---|---|---|
| 202606 | 3.759 / 6.841 / 16.923 | 1.714 / 2.317 / 10.019 |
| 202607 | 5.662 / 7.050 / 16.477 | 2.542 / 3.013 / 11.586 |
| 202608 | 3.647 / 7.546 / 14.812 | 2.162 / 2.871 / 10.825 |

Agosto/2026 DF já constava com os mesmos hashes; não foram duplicados os
indicadores existentes. As planilhas contêm microdados na fonte, mas a Silver
guarda apenas quantidades agregadas por UF, espécie e motivo/despacho. Não
inferir residência municipal, concessão individual nem relação com qualquer
CNJ a partir de UF ou data.

O IpeaJus foi descrito historicamente em nota do [repositório oficial do Ipea](https://repositorio.ipea.gov.br/bitstreams/31e22baa-3bae-4019-a4a3-63a66d7b1d1e/download).
Nesta execução não foi localizado API, catálogo ou pacote de microdados público
atual para integração. Um rascunho de solicitação foi preparado em
`docs/RASCUNHOS_SOLICITACAO_ACESSO.md`; não foi enviado.
## Verificação adicional — 08/10/2026

- CJF, base TRF1: consultados os primeiros 10 CNJs de
  `data/piloto-manifesto-luna-200.csv`, com até duas páginas por consulta.
  Resultado: 10 consultas sem resultado, zero documentos/vínculos novos.
  Não é amostra representativa nem prova de ausência de decisões.
- No espelho JEF1 `000046005`, “Acesse Aqui” é o endereço genérico
  `https://pje2g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam`.
  Não fornece link direto ao acórdão. O acesso de verificação foi interrompido
  por redirecionamento fora do host permitido, sem contorno ou tentativa de login.
- Consultas e Bronze persistidos em `data/bpc-consolidado-luna-20261007.sqlite`;
  backup anterior em `data/backup-pre-cjf-trf1-20261008.sqlite`.
  Conteúdo processual continua limitado ao que cada fonte efetivamente publicou;
  nenhum texto novo foi enviado à IpeaIA.

### Ampliação Comunica PJe — 08/10/2026

No SQLite local `data/bpc-consolidado-luna-20261007.sqlite`, retomei 64 CNJs
pendentes do manifesto `data/manifesto-comunica-200-20261008.csv` e consultei
mais 200 CNJs inéditos do manifesto
`data/manifesto-comunica-200b-20261008.csv` (semente `20261009`; quotas 100/50/50;
estratos por ano e assunto). Ao final, os manifestos somam 400/400 consultas
registradas: 68 CNJs tiveram
publicação e 332 ficaram sem resultado, sem erros finais ou bloqueios. Foram
observadas 110 comunicações, todas novas pela chave processo + hash; o total
subiu de 110 para 220. O rótulo publicado em 10 CNJs distintos incluiu sentença
em 7, decisão em 4 (um CNJ sobreposto) e acórdão em nenhum. Revisão local de dez
textos não encontrou motivo explícito de indeferimento administrativo; os
textos são atos processuais parciais, em maioria sobre demora/andamento, não
autos completos. Os grupos são definidos pela sede do órgão julgador, não pela
residência. A coleta interrompida anterior conserva status `falhou`; seu gzip
foi preservado e não passou a leitura integral. Backup consistente via API
SQLite, IDs das execuções, resultado por grupo/ano e checks estão em
`RELATORIO_AMPLIACAO_COMUNICA_20261008.md`. Nenhum processo ou extração IA foi
alterado, nenhum texto foi enviado à IpeaIA e não houve mudança de schema.

### Auditoria e recuperacao delimitada do Bronze Comunica - 08/10/2026

O arquivo da coleta `8ed0515fabfb45b89671e6768f730c02` foi preservado sem
alteracao. Foram decodificadas 136 linhas JSON completas antes do EOF, todas
com HTTP 200 (30 encontradas, 106 sem resultado), mas o gzip esta sem trailer
e CRC verificavel; por isso nenhuma dessas respostas conta como Bronze
integralmente validada. As outras 64 consultas do manifesto passaram a ter
Bronze integra em coletas posteriores concluidas. A lista exata das 136
consultas consta no manifesto local ignorado pelo Git
`data/recuperacao-bronze-comunica-8ed0515f-20261008.csv`.

A coleta nova `28a0d9a73da5405f833f2acb1dc49334` concluiu com 136 linhas gzip
validas, HTTP 200 em todas, 30 encontradas, 106 sem resultado, zero erros e
zero bloqueios. Foram observadas 41 comunicacoes, todas ja presentes pela chave
processo/hash (zero novas); o banco permaneceu com 220. A API retorna o estado
atual da publicacao; nao se afirma que a resposta atual reproduza a resposta
original. Nao foram repetidos bloqueios nem contornado CAPTCHA.

A revisao textual de dez publicacoes esta registrada em
`data/revisao_comunicacoes_manifesto_20261008.csv`, local e fora do Git; contem
CNJ, ID/hash, rotulo, criterios, conclusao e indicadores de fundamentacao,
dispositivo e motivo administrativo explicito, sem nomes, CPF ou citacoes.

### Modo local de analise textual de comunicacoes - 08/10/2026

O contrato foi atualizado antes do modo de analise. `ipeaia-comunicacoes-preparar`
prepara texto minimizado sem chamadas externas; `ipeaia-comunicacoes-importar`
valida localmente vinculo processo/comunicacao/hash/trecho e grava resultado
novo pendente, sem alterar a triagem `triagem_bpc` nem substituir extracoes.
O tipo e `comunicacao_bpc_texto`, prompt `ipeaia_comunicacoes_v1`. A previa
local gerada contem 20 comunicacoes de 7 processos, ate 60.000 caracteres
redigidos, sem CNJ, CPF, email ou URL detectados; segue necessaria revisao
humana de privacidade antes de qualquer envio futuro. Nenhum texto foi enviado
a IpeaIA e o banco continua com zero extracoes textuais.
## Verificação e coleta complementar — 08/10/2026 (correções)

- TRF6: `trf6-pesquisa --query LOAS --origens TRF6 --limit 5 --paginas 3
  --timeout 30` coletou cinco URLs/documentos e cinco versões novas, pulando
  cinco URLs já concluídas. Corpus passou de 168 para 173 versões; processos
  continuam 16.737, comunicações 220. Origem suplementar, não cobertura DF/RIDE.
- TRF3: o documento público `https://web.trf3.jus.br/acordaos/Acordao/BuscarDocumentoPje/344467700`
  foi confirmado na leitura web, mas o download direto pelo coletor expirou
  após timeout de 25 segundos; coleta `falhou`, zero documentos importados.
  Não significa ausência de texto publicado ou autorização para contornar acesso.
- A página oficial SJPA de inteiro teor
  `https://www.trf1.jus.br/sjpa/processual/inteiro-teor-de-sentencas-e-decisoes`
  indica aba inteiro teor na consulta processual e disponibilidade por vara.
  Seu link observado leva a `https://processual.trf1.jus.br/consultaProcessual/numeroProcesso.php?enviar=ok&secao=PA`.
  A página foi legível na pesquisa web; o acesso direto de investigação expirou
  em 20 segundos. Nenhum processo foi consultado nem documento importado dessa
  rota. Não extrapolar disponibilidade no Pará para Brasília ou autos completos.

### Piloto Comunica, diários históricos TRF1, PJe e CRPS — 08/10/2026

O novo manifesto `data/manifesto-comunica-luna-400-20261008.csv` selecionou
400 CNJs inéditos (200 núcleo Brasília, 100 Formosa, 100 Luziânia), com seed
`20261010`, estratos ano/assunto e filtros TRF1, G1/JE, públicos, assuntos
6114/11946/11947 e grupo pelo município do órgão DataJud. Entre 3.135 elegíveis,
as quotas foram preenchidas sem sobreposição; manifestos anteriores e consultas
`encontrado`/`sem_resultado` foram excluídos. A API Comunica respondeu HTTP 503
em sequência; a execução `b6af7ba3ae05425389c52ea6128eb070` parou após 10 CNJs
de Formosa (2018/2021), cinco tentativas limitadas por CNJ, zero publicações e
390 CNJs pendentes. A Bronze parcial foi preservada, não validada como gzip
íntegro. Não considerar esse lote como publicação inexistente. Integridade,
grupos/anos, hashes e retomada estão em
`RELATORIO_COLETA_COMUNICA_DIARIOS_LUNA.md`.

A página oficial [Diários da Justiça TRF1](https://www.trf1.jus.br/trf1/diarios-da-justica/diarios-da-justica)
separa DJEN atual, atos administrativos e acervos e-DJF1 judiciais de
1990–2020. Não usamos cadernos administrativos como publicações judiciais nem
tratamos DJEN atual como arquivo histórico. Para um piloto de 30 CNJs antigos
sem Comunica, o endpoint judicial 2015–2020 teve falha DNS/502; o link
2009–2015 teve HTTP 500/timeout; a Biblioteca oficial de 1990–2008 falhou na
validação TLS local. Nenhuma edição foi baixada e nenhum processo foi
classificado como sem publicação. O piloto está em
`data/piloto-diarios-trf1-cnjs-luna-20261008.csv`; datas DataJud orientam a
busca, mas não determinam a data da publicação. Não houve extração PDF/OCR,
vínculo documental ou mudança do contrato.

O [formulário público PJe/TRF1](https://pje1g-consultapublica.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam)
abriu HTTP 200, sem login ou redirecionamento. Cinco CNJs existentes foram
submetidos pela consulta pública; as respostas não confirmaram metadados
estruturados nem link/identidade de documento. O script hCaptcha estava
presente, sem desafio apresentado; não foi resolvido nem contornado. A página
alerta que segredo de justiça ou dado incorreto pode resultar em vazio, então
resultado ausente não prova inexistência. Não afirmar acesso a autos completos.

A orientação oficial [Consulta Jurisprudência CRPS](https://www.gov.br/previdencia/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/conselho-de-recursos-da-previdencia-social/consulta-jurisprudencia)
informa que o portal contém decisões administrativas e filtra por tipo de
processo, unidade julgadora, objeto recursal, espécie/tipo de benefício e
palavras na ementa/voto; o acesso exige conta gov.br. O pesquisador deve
consultar diretamente com sua conta, registrar os metadados/arquivos úteis e
não compartilhar credenciais. Decisão CRPS não pode ser ligada a motivo de
processo judicial sem evidência individual explícita.

### Atualização PJe/TRF1 — conteúdo individual confirmado (08/10/2026)

A tentativa anterior acima não demonstrava indisponibilidade da fonte: a ação
AJAX correta é a publicada em `executarPesquisa`, diferente do ID do botão.
Na sessão pública observada, `executarReCaptcha` indica explicitamente
`if (false) { hcaptcha.execute(); return false; }`; desafio ativado interrompe
a automação, sem contorno. Não houve login ou uso de credencial.

O coletor `python -m bpc_ingestion.pje_public` segue somente links oficiais
publicados no resultado CNJ e valida detalhe, cabeçalho e ID da assinatura.
Foram incorporados **158 textos, vinculados a 73 processos existentes**;
nenhum processo foi criado. Corpus local: 693 documentos e 166 vínculos.
Não são autos completos: apenas Sentença/Decisão/Despacho/Acórdão HTML da
primeira página e dentro do limite explícito. CRPS continua administrativo.

Origem do CNJ: 71 casos das três sedes Brasília/Formosa/Luziânia e dois de
Goiânia/Tocantins selecionados pelo órgão atual DataJud. Não inferir residência
nem promover todos a DF/RIDE. Datas de juntada não viram datas de decisão.
Texto/link retidos na API para revisão de privacidade, sem envio à IpeaIA.
Detalhes e verificações: `RELATORIO_PJE_PUBLICO_20261008.md` e CONTRATOS.md.

Atualização histórica no mesmo dia: mais 45 textos válidos, totalizando 203
documentos PJe em 85 processos (corpus 738/vínculos 211). A rodada 2020–2022
parou na 12ª consulta: documento 469433861 apresentou CNJ diferente do
solicitado. Foi rejeitado, não vinculado; os outros 38 casos do manifesto não
foram consultados. Conferência integral de 203 documentos e 538 gzip,
183 testes aprovados, banco íntegro. Três CNJs têm origem fora das três sedes
principais; não inferir residência. Mantém-se conteúdo individual público,
não autos completos, sem envio à IA nem atualização do pacote remoto.

## Censo SUAS municipal — coleta pública 2025 (12/10/2026)

O [portal oficial Censo SUAS — Bases e Resultados](https://aplicacoes.mds.gov.br/sagi/snas/vigilancia/index2)
publica arquivos anuais sem login. Foram baixados os ZIPs de [CRAS 2025](https://aplicacoes.mds.gov.br/snas/defeso/censosuas/2025/1_CRAS.zip)
e [Postos de Cadastramento 2025](https://aplicacoes.mds.gov.br/snas/defeso/censosuas/2025/8_POSTO_DE_CADASTRAMENTO.zip),
com 18.561.593 e 5.109.111 bytes, respectivamente. A integridade ZIP foi
verificada e os SHA-256 registrados em `CONTRATOS.md`. Os arquivos locais em
`data/raw/mds_censo_suas_2025/` não devem ser commitados: cada ZIP também contém
arquivos de recursos humanos e sintaxes SPSS, que não são necessários para esta
análise.

O importador lê apenas o CSV `Dados Gerais` e agrega por IBGE7/UF/município e
identificador único de unidade. Na base consolidada local ficaram 8.903 CRAS em
5.547 municípios e 3.383 postos em 3.010 municípios. No recorte estadual DF/GO/MG,
os totais são 1.591 CRAS (32/305/1.254) e 554 postos de cadastramento
(18/110/426). São contagens de unidades, não de famílias, trabalhadores ou
atendimentos. Nenhuma linha do CSV de RH, pessoa ou processo foi para a Silver;
nenhuma ligação foi feita por município do órgão julgador.

A tabela `indicadores_suas_municipio` foi adicionada ao contrato v0.10 e à
migração aditiva 0008. O banco local passou na verificação de integridade e não
tem violações de chave estrangeira. A fonte pode contextualizar infraestrutura
socioassistencial, mas não revela o motivo de judicialização, concessão de BPC,
residência do requerente ou acesso individual a serviço. A nova coleta não foi
enviada à IpeaIA e ainda não foi exportada para o pacote remoto.

### TJGO — consulta processual pública

O portal oficial [Projudi/TJGO](https://projudi.tjgo.jus.br/) anuncia a opção
“Pública processual”. O formulário dessa opção respondeu HTTP 200, mas contém
campo `g-recaptcha-response`; não submeti CNJs nem tentei resolver/contornar
CAPTCHA. Nenhum texto ou processo foi importado. O acesso fica para consulta
assistida, enquanto os dados DataJud TJGO já existentes permanecem metadados e
movimentos, sem inteiro teor.

### MDS — CadÚnico/CECAD e tempo de concessão BPC no VIS DATA (12/10/2026)

O [CECAD 2.0](https://cecad.cidadania.gov.br/tab_cad.php) oferece o TABCAD
agregado com marcações de famílias e pessoas que recebem BPC. A interface
exibe variável BPC e filtros, mas antes de gerar a tabulação/download pede
aceite do “Termo de Compromisso de Manutenção de Sigilo”. Não aceitei nem
submeti a consulta, pois isso exige compromisso nominal do pesquisador. Nenhum
dado foi extraído. Dados identificados do CadÚnico continuam fora do escopo e
dependem de autorização específica.

O [Observatório do Cadastro Único](https://paineis.mds.gov.br/public/extensions/observatorio-do-cadastro-unico/index.html)
e o IVCAD são apresentados pelo MDS como ferramentas públicas de consulta de
agregados; a FAQ ministerial descreve exportação dos dados dos gráficos. Não
consegui fazer a exportação nesta execução: o controle de interface interrompeu
a navegação no Brave antes de abrir a página porque não conseguiu validar com
segurança a URL atual da janela. Na retomada, a interface CUA não apresentou
nenhum app ou navegador (`apps=[]`, `browsers=[]`) e recusou abrir a aba IAB.
Não houve exportação nem chamada a endpoint interno do Qlik. A fonte continua
pendente de navegador acessível; enquanto isso, prossegui por endpoint público
alternativo do VIS DATA, sem login.

Como próxima fonte sem credencial nem termo, consultei o [VIS DATA 3 — Tempo
médio de concessão regionalizado do BPC](https://aplicacoes.cidadania.gov.br/vis/data3/v.php?q%5B%5D=oNOhlMHqwGZsemeZ6au8srNfiZmvm7ml2eiyp7jEsbbp).
O HTML público contém 330 registros mensais para Norte, Nordeste, Sudeste, Sul
e Centro-Oeste, de janeiro/2021 a junho/2026, com médias separadas para PcD,
idosos e total. No Centro-Oeste em junho/2026, a origem reporta 187, 109 e 152
dias, respectivamente. A amostra está em `data/raw/visdata_bpc_tmc/` (HTML,
CSV derivado e manifesto com hash); a pasta `data/` é local/ignorada pelo Git.
São médias administrativas agregadas por região, não tempo de tramitação
judicial, nem medida específica do DF/RIDE e tampouco evidência sobre processo
individual. Mantive a série fora da Silver e sem vínculo ao DataJud; não foi
enviada à IpeaIA.

### MDS — beneficiários e valores do BPC por município pagador (VIS DATA 3)

Usei a visão pública [“Benefício de Prestação Continuada BPC — por município pagador” do VIS DATA 3](https://aplicacoes.cidadania.gov.br/vis/data3/). A página mostra “Usuário não autenticado”; a tabela oferece exportação CSV e foi consultada sem login. Para cada um dos 34 códigos municipais do recorte DF/RIDE, coletei a tabela anual de 2004–2024 (714 observações) e a série mensal de janeiro/2004 a abril/2024 (8.243 observações), com contagens de beneficiários PcD e idosos, valores pagos por grupo e totais. Na série mensal, 32 municípios têm as 244 referências; o retorno para Cabeceira Grande não contém 40 meses e o de Vila Propício não contém 13. Esses intervalos ausentes foram mantidos como ausentes, nunca convertidos em zero. CSVs, 68 respostas JSON individuais e manifestos com hashes estão em `data/raw/mds_visdata_bpc_municipio_ride/`.

O campo territorial representa município pagador, não necessariamente residência do beneficiário; portanto não pode ser usado como localização de requerentes ou litigantes. São contagens e valores administrativos agregados, não casos judiciais, nem prova de elegibilidade ou de causa de judicialização. Mantive o conjunto fora da Silver e da IpeaIA. A série anual termina em 2024 e, nesta consulta mensal, a última referência retornada é abril/2024.

### IBGE — rendimento domiciliar per capita municipal na RIDE-DF (Censo 2022)

Também consultei a [tabela 10295 do SIDRA](https://sidra.ibge.gov.br/tabela/10295), usando as variáveis de rendimento nominal médio mensal per capita (13431) e mediano (13534), com totais de sexo, cor/raça e idade. A extração pública contém 68 valores para os mesmos 34 municípios e está em `data/raw/ibge_censo2022_ride/` (respostas JSON, metadados, CSV e `manifesto_rendimento.json`). A tabela define uma população específica: moradores em domicílios particulares permanentes ocupados, excluindo pensionistas, empregados domésticos e seus parentes; portanto não é renda média de todas as pessoas nem dos litigantes. Os valores são municipais e agregados, não permitem inferir elegibilidade ao BPC e não foram inseridos na Silver ou enviados à IpeaIA.

### IBGE — pessoas com deficiência por grupo etário na RIDE-DF (Censo 2022)

Como indicador contextual adicional, consultei a [tabela 10131 do SIDRA](https://sidra.ibge.gov.br/tabela/10131), disponibilizada pelo IBGE para o Censo 2022. A tabela fornece contagens de pessoas residentes de 2 anos ou mais por grupo etário e existência de deficiência, nos municípios. Extraí a variável 11852 para os mesmos 34 códigos municipais (DF, 29 de GO e quatro de MG) usados no recorte RIDE-DF. A amostra está em `data/raw/ibge_censo2022_ride/`: 2.754 linhas no CSV (27 categorias/grupos etários × três categorias de deficiência × 34 municípios), JSON da API, metadados e `manifesto_deficiencia.json`. Os 131 valores publicados como `-` foram mantidos literalmente. Em 115 grupos com as três contagens numéricas, total e soma das categorias PcD/sem deficiência diferem em uma pessoa, consistente com arredondamento; não alterei os valores oficiais. É estatística populacional agregada do Censo, não critério de elegibilidade ao BPC, perfil de requerentes ou prova de residência dos litigantes; não foi integrada à Silver nem enviada à IpeaIA.

### IBGE — população residente por idade na RIDE-DF (Censo 2022)

Consultei a [tabela 9514 do SIDRA](https://sidra.ibge.gov.br/tabela/9514),
pela API pública do IBGE, que fornece população residente por idade no Censo
2022. Usei a [lista oficial da Sudeco para a RIDE-DF](https://www.gov.br/sudeco/pt-br/acesso-a-informacao/perguntas-frequentes-1/RIDE)
e os códigos do serviço oficial de localidades: DF, 29 municípios de Goiás e
quatro de Minas Gerais. Foram preservadas 4.556 linhas de categorias etárias
em `data/raw/ibge_censo2022_ride/`, além das respostas JSON, metadados SIDRA e
manifesto. Os 53 valores `-` permanecem como publicados, sem interpretação ou
conversão para zero. É contexto populacional de 2022, não residência dos
litigantes, perfil dos processos ou elegibilidade individual; não foi carregado
à Silver nem enviado à IpeaIA.

### CJF/JEF1 — pesquisa temática pública BPC (13/10/2026)

Na [pesquisa pública de jurisprudência do CJF/JEF1](https://jurisprudencia.cjf.jus.br/trf1/index.xhtml),
busquei `BPC`; no momento da consulta, o portal reportou 1.092 resultados em 37
páginas. Ampliei a paginação do coletor para permitir retomada por página e
coletei as páginas 1–37 sem autenticação: 1.092 acórdãos, todos com texto e
CNJ explícito. Foram acrescentadas 1.092 versões, sem chaves duplicadas; sete
documentos foram vinculados por CNJ explícito a seis processos que já estavam
na população. Não foram criados processos. As respostas brutas totalizam 42
arquivos HTML/XML gzip, todos descompactados e verificados. O corpus total
passou de 1.058 para 2.150 documentos; processos permaneceram em 16.737 e os
vínculos subiram de 531 para 538. Esse corpus tem decisões publicadas e não é
amostra representativa nem inteiro teor universal dos autos da população.
Backup anterior às coletas: `data/backup-pre-cjf-tematico-20261013.sqlite`
(integridade validada). Nenhum texto foi enviado à IpeaIA.

### TNU e TRF2/TRF4/TRF5/TRF6 — expansão do corpus público (13/10/2026)

Retomei as pesquisas oficiais por `LOAS`, sem autenticação, para consultar os
resultados seguintes ainda não cobertos: 50 URLs na TNU e em cada TRF2, TRF4,
TRF5 e TRF6. Foram persistidas 100 decisões TNU, 48 TRF2, 50 TRF4, 50 TRF5 e
50 TRF6 (298 versões novas). Todos os 298 arquivos brutos associados estavam
presentes e passaram a leitura gzip. Esses acórdãos/decisões são corpus
suplementar: nenhum novo processo foi criado nem novo vínculo com a população
foi presumido. Os totais por fonte passaram a TNU 266, TRF2 129, TRF4 132,
TRF5 130 e TRF6 135 documentos.

### PJe/TRF1 — lote adicional de processos (13/10/2026)

A consulta processual pública foi executada sem login nem CAPTCHA para 50
processos pendentes, em rodízio entre núcleo Brasília (17), Formosa (17) e
Luziânia (16). Em 32 processos havia documentos-alvo e em 18 não havia
documentos públicos do tipo sentença/decisão/despacho/acórdão na página
consultada. Foram gravados 67 documentos novos com identidade confirmada pelo
CNJ no cabeçalho e vínculos explícitos aos 32 processos. Todos os 218 arquivos
brutos HTML gzip desse lote foram validados; nenhum caso ultrapassou o limite de
10 documentos por processo. O corpus PJe passou de 523 para 590 documentos; a
população de processos permaneceu inalterada. A seleção pendente por grupo e a
consulta de primeira página não constituem amostra representativa nem garantem
autos completos.

O snapshot anterior (2.515 documentos, 605 vínculos, 16.737 processos; SQLite
íntegro e sem violações FK) foi copiado para
`data/backup-pos-coletas-20261013.sqlite`, 513.933.312 bytes, SHA-256
`8d0ffdd6b63232db7e509b34c8cee66a09f8190f41555cc965f8cb6aff110924`. Os dados
continuam locais e fora do Git; nenhuma extração foi enviada à IpeaIA.

### Novos lotes de pesquisa judicial pública (13/10/2026)

Retomei as pesquisas TNU e TRF2/TRF4/TRF5/TRF6 por `LOAS`, consultando URLs
pendentes: TNU +80, TRF2 +47, TRF4 +50 e TRF5 +50 documentos. No TRF6, além do
lote `LOAS` (+50), busquei `BPC` (+50). Foram 327 documentos novos nesses lotes,
sem criação de processos nem vínculo presumido à população. Totais atuais:
2.853 documentos e 618 vínculos; por fonte, TNU 346, TRF2 176, TRF4 182, TRF5
180 e TRF6 235. `integrity_check=ok`, sem violações FK.

Uma segunda tentativa de ampliar o PJe/TRF1 parou após erro de identidade
documental do coletor: 15 processos foram tentados, 11 documentos novos foram
preservados e o coletor interrompeu ao detectar divergência no cabeçalho CNJ.
Os demais casos desse lote não foram consultados; não houve tentativa de
contornar a validação. O corpus PJe totaliza 601 documentos. Decisões de outros
TRFs e da TNU continuam sendo jurisprudência suplementar publicada, não inteiro
teor universal dos autos nem amostra representativa.

### Retomada de coleta pública nos TRFs (13/10/2026)

Sem credenciais, ampliei o corpus de decisões publicadas com buscas textuais nos
portais oficiais do TRF4, TRF5 e TRF6. Os lotes confirmados nesta retomada
adicionaram 550 decisões `LOAS` e 12 decisões `BPC` do TRF5; 50 `BPC`, 50
`LOAS` e 41 resultados da expressão `benefício assistencial` do TRF6; e 50
decisões `LOAS` do TRF4 (753 documentos novos no conjunto). No último termo do
TRF6, 50 URLs foram consultadas; 41 retornaram documento publicável. Não houve
criação de processos nem vínculo presumido entre decisões de jurisprudência e
a população de processos. O TRF4 teve uma tentativa posterior interrompida por
timeout de rede; os documentos já coletados permaneceram preservados. Uma
tentativa executada sem apontar o SQLite tentou conectar ao PostgreSQL local e
falhou; as coletas foram retomadas explicitamente no SQLite, sem sobrescrever
nem perder dados.

O MCP `mcp-juridico-brasil` não foi tratado como nova fonte: sua descrição
indica que consulta o mesmo DataJud já integrado, não o inteiro teor dos autos.

Estado verificado ao final: 23.026 `documentos_publicos`, 16.737 processos e
715 vínculos explícitos em `documento_processos`. Totais de documentos por
fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU 439; arquivo TRF1 7; TRF2
253; TRF4 617; TRF5 1.320; TRF6 841. `PRAGMA quick_check` retornou `ok` e
`foreign_key_check` não apontou violações. Os 250 arquivos brutos mais recentes
foram descompactados e validados com sucesso. Snapshot consistente:
`data/backup-pos-retomada-20261013-1725.sqlite` (23.026 documentos, 715
vínculos, SHA-256 `E8AF584F6B66ECB20F81CFCBF44BCF8528D4A3733B14C1B93FACD9BE64A13A12`).
As fontes seguem sendo complementares: acórdãos e decisões publicados não
equivalem ao inteiro teor completo dos processos nem formam amostra
representativa. Nenhuma extração foi enviada à IpeaIA.

### Atualização da coleta TRF6 e snapshot (13/10/2026)

Continuei no TRF6 com a expressão `benefício de prestação continuada`, em 11
lotes idempotentes; foram persistidas 424 decisões novas. A busca percorreu até
a página 100, limite configurado do coletor, portanto isso não prova que todo o
acervo do tribunal foi esgotado. No CJF/JEF1, as páginas 201–220 para `LOAS` e
442–461 para `benefício assistencial` retornaram zero documentos. Nenhum texto
foi enviado à IpeaIA e não foi presumido vínculo com processos da população.

O snapshot mais recente substitui o estado intermediário registrado acima:
23.450 `documentos_publicos`, 16.737 processos e 717 vínculos explícitos.
Totais por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU 439; arquivo
TRF1 7; TRF2 253; TRF4 617; TRF5 1.320; TRF6 1.265. `PRAGMA quick_check=ok`,
nenhuma violação em `foreign_key_check` e os 320 arquivos brutos mais recentes
passaram validação gzip. Snapshot validado:
`data/backup-pos-retomada-20261013-1753.sqlite`, 23.450 documentos e 717
vínculos, SHA-256
`D6AAAAAD3D6E332AA2A316F61DD96358ADB4A96DAD764392AC7E032E0EDC5453`.

### Retomada TRF6 a partir da página 101 (13/10/2026)

O portal informou 5.227 resultados (`benefício de prestação continuada`), em
523 páginas de 10 itens. Para não parar artificialmente na antiga janela de
100 páginas, acrescentei ao comando `trf6-pesquisa` o argumento
`--pagina-inicial`. A busca foi retomada da página 101 até a 177 em 11 lotes,
que persistiram 527 documentos novos. O processo mantém paginação idempotente;
somente números CNJ explícitos na página do tribunal podem vincular um
documento a processo existente. A população continuou em 16.737 processos; os
vínculos explícitos subiram de 717 para 721. A próxima página pendente é 178.

Snapshot mais recente, que substitui o anterior: 23.977 `documentos_publicos`;
por fonte, CJF/TRF1 18.535, PJe/TRF1 601, STJ 413, TNU 439, arquivo TRF1 7,
TRF2 253, TRF4 617, TRF5 1.320 e TRF6 1.792. `PRAGMA quick_check=ok`, zero
violações FK e 527 arquivos brutos recentes validados por gzip. Backup
`data/backup-pos-retomada-20261013-1808.sqlite` (23.977 documentos, 721
vínculos), SHA-256
`0ADC3CCADA6313D66CBE2C458F6743C6C401A9ABE67736EF9FF275765C5F1C73`.

### Busca TRF6 concluída — 13/10/2026

A consulta pública `benefício de prestação continuada` reportou 5.227 resultados
em 523 páginas. A paginação foi conferida em sequência, sem lacunas das páginas
1–523; itens já baixados foram ignorados de forma idempotente. Foram obtidos
5.026 documentos publicáveis do TRF6 nessa origem. Os 5.227 resultados do portal
não equivalem a documentos únicos ou todos acessíveis: alguns não fornecem
inteiro teor. O corpus contém decisões publicadas, não autos completos nem uma
amostra representativa da população de processos.

Na busca principal TRF6 foram persistidos 5.026 documentos. Sondagens
separadas do mesmo portal acrescentaram 10 documentos da origem `TRU6` e 9 das
`Turmas Recursais`; em lotes posteriores, mais 7 documentos da TRU6 e 20 das
Turmas Recursais. A última sondagem para `Varas Federais` não encontrou links
na primeira página. Uma URL das Turmas não tinha documento disponível. A
contagem física continua agrupada sob `trf6_jurisprudencia`, portanto esses
subtotais foram medidos pelos lotes, não por uma coluna de origem no esquema.

Estado validado no snapshot: 27.257 `documentos_publicos`, 16.737 processos e
740 vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
439; arquivo TRF1 7; TRF2 253; TRF4 617; TRF5 1.320; TRF6 5.072. `PRAGMA
quick_check=ok` e `foreign_key_check` sem violações. Snapshot consistente:
`data/backup-pos-retomada-20261013-1945.sqlite` (SHA-256
`F81F831C70529DD3D5CCA8C3CEE2B812E1C1AFF241EF377C7F9B72CF950EE8D4`).

Dez documentos TRF6 seguem registrados como falhos: dois cabeçalhos sem CNJ
único, um timeout e sete layouts não reconhecidos. Não foram contornados nem
reprocessados. Os itens sem texto disponível permanecem marcados
`sem_resultado`; nenhum envio à IpeaIA ocorreu nessa coleta.

### Outras fontes públicas — retomada 13/10/2026

- **Portal da Transparência/CGU:** com o token já configurado no ambiente
  local (nenhuma nova credencial solicitada), ampliei julho/2026 de Brasília
  para os 34 municípios oficiais da RIDE-DF: DF, 29 municípios goianos e quatro
  mineiros. A API respondeu para os 34; Brasília já existia, então foram
  acrescentados 33 registros agregados. O campo territorial é município pagador,
  não prova residência de beneficiário ou litigante. O snapshot registra 34
  municípios na competência 202607.
- **TRF3:** a consulta pública oficial por número de processo e o portal de
  jurisprudência continuam descritos pelo Tribunal. A tentativa direta nesta
  execução expirou após 35 segundos, como em tentativas anteriores. Um resultado
  oficial indexado pelo mecanismo de busca apresentou texto de acórdão BPC, mas
  não foi possível baixá-lo pelo coletor local nem preservá-lo em Bronze; não
  contei esse texto como documento ingerido. A fonte permanece bloqueada para
  coleta automatizada neste ambiente, não ausente.
- **INSS:** tentei as competências 202609 para indeferimentos e concessões; o
  catálogo não continha recurso XLSX correspondente em nenhum dos dois datasets.
  Não houve ingestão. As tabelas locais seguem cobrindo janeiro–agosto/2026 para
  DF, GO e MG.

Nenhum documento judicial dessas tentativas foi enviado à IpeaIA. Os portais
TJGO/TJMG e CECAD seguem exigindo CAPTCHA/termo ou interação do pesquisador;
não os automatizei nem tentei contornar as proteções.

### TRF6 — continuação das Turmas Recursais (13/10/2026)

Retomei a busca pública por `benefício de prestação continuada` nas Turmas
Recursais a partir da página 45. Foram percorridas sequencialmente as páginas
45–93 e persistidos 443 documentos novos; algumas URLs não retornaram documento
publicável. O portal informa 7.611 resultados em 762 páginas, portanto a coleta
continua incompleta e pode ser retomada na página 94. Nenhum processo da
população foi criado ou vinculado sem número CNJ explícito; nenhum texto foi
enviado à IpeaIA.

O banco consolidado tem 28.232 `documentos_publicos`, 16.737 processos e 762
vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
592; arquivo TRF1 7; TRF2 253; TRF4 617; TRF5 1.320; TRF6 5.894.
`PRAGMA quick_check=ok` e `foreign_key_check` sem violações. Snapshot validado:
`data/backup-pos-retomada-20261013-2011.sqlite` (SHA-256
`DB8A9D75D8DFADAA3D8973C17DFB7C21AEDCA83EBF4506B6A912C46038C95DAC`).

### Continuação TRF6 e TNU (13/10/2026, 20:26)

As Turmas Recursais do TRF6 avançaram até a página 114 da busca de 7.611
resultados. As páginas 45–114 acrescentaram 643 documentos publicáveis; próxima
página a consultar: 115. A busca não está completa (762 páginas reportadas pelo
portal).

Na TNU, a expressão `benefício assistencial` acrescentou 174 documentos em
lotes idempotentes, cobrindo resultados até a página 51. A coleta foi encerrada
ao detectar o artigo `771747762500608133306200300587` sem identidade documental
estável/cabeçalho CNJ. Documentos anteriores foram preservados; não houve
contorno ou nova tentativa desse item. Outros termos e fontes seguem disponíveis
para exploração, sujeitos às mesmas validações.

Snapshot consolidado: 28.606 `documentos_publicos`, 16.737 processos e 764
vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
766; arquivo TRF1 7; TRF2 253; TRF4 617; TRF5 1.320; TRF6 6.094.
`PRAGMA quick_check=ok`; `foreign_key_check` sem violações. Backup validado:
`data/backup-pos-retomada-20261013-2026.sqlite`, SHA-256
`996AA9C19BEADF32701693044920189074A54667E87C8A77D35EB97C0B612FAA`.
Nenhum documento ou extração foi enviado à IpeaIA.

### TRF6 — retomada das Turmas Recursais (13/10/2026, 20:37)

Continuei a consulta `benefício de prestação continuada` nas Turmas Recursais
do TRF6. Os lotes idempotentes avançaram da página 114 até a 162 e acrescentaram
447 documentos publicáveis desde o snapshot das 20:26. Como o limite de URLs
terminou dentro da página 162, a próxima execução deve reiniciar nessa página
para pular itens já concluídos e cobrir os restantes. O portal ainda informa
762 páginas; a busca continua incompleta.

Snapshot consolidado: 29.053 `documentos_publicos`, 16.737 processos e 772
vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
766; arquivo TRF1 7; TRF2 253; TRF4 617; TRF5 1.320; TRF6 6.541.
`PRAGMA quick_check=ok`; `foreign_key_check` sem violações. Backup:
`data/backup-pos-retomada-20261013-2037.sqlite`, SHA-256
`DCB431CA8EF2748755182B29344A59B2601187B4C7253F6FA3EFBE745DA724EA`.
Nenhum documento foi enviado à IpeaIA.

### TRF6 — continuação até a página 209 (13/10/2026, 20:49)

As Turmas Recursais avançaram até a página 209 e acrescentaram 198 documentos
publicáveis desde o snapshot anterior. A última execução terminou durante a
página 209; retomar nessa página para pular coletas já concluídas. A busca do
portal permanece incompleta (7.611 resultados/762 páginas informados).

Snapshot validado: 29.501 `documentos_publicos`, 16.737 processos e 781
vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
766; arquivo TRF1 7; TRF2 253; TRF4 617; TRF5 1.320; TRF6 6.989.
`PRAGMA quick_check=ok`; `foreign_key_check` sem violações. Backup:
`data/backup-pos-retomada-20261013-2049.sqlite`, SHA-256
`A3CB71277CFAFC9C86E7CF625540A7ACA5A729D9324BA747B8D7CBCA7E108D58`.
Nenhum documento foi enviado à IpeaIA.

### Retomada TRF6 e complemento TRF2 — 13/10/2026, 21:31

Retomei as Turmas Recursais do TRF6 pela página 256 da consulta
`benefício de prestação continuada`, usando lotes idempotentes de até 50 URLs.
O avanço chegou à página 328; desde o snapshot anterior das 20:49, entraram
1.155 documentos TRF6. Nesta retomada foram acrescentados 685 documentos. A
busca segue incompleta: o portal informou 7.611 resultados em 762 páginas.
Um item falhou por layout não reconhecido (`381779215907343497116025508552`);
foi registrado como falha e não houve tentativa de contorno. O timeout anterior
também permanece sem repetição.

O complemento do TRF2 foi retomado até concluir o lote que estava em andamento:
foram 154 documentos novos no total desta rodada TRF2, elevando a fonte de 253
para 407 documentos. Nenhum conteúdo foi enviado à IpeaIA.

Snapshot validado: 30.810 `documentos_publicos`, 16.737 processos e 807
vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
766; arquivo TRF1 7; TRF2 407; TRF4 617; TRF5 1.320; TRF6 8.144.
`PRAGMA quick_check=ok`; `foreign_key_check` sem violações. Backup:
`data/backup-pos-trf6-20261013-2131.sqlite`, 1.165.926.400 bytes, SHA-256
`8A69372B0BCE3389FDAD074EAD489D1DE6469B87D34E82346ECEC101AE8E959D`.
Naquele snapshot, próxima página TRF6: 328, para que URLs concluídas fossem
puladas e os itens restantes da página fossem cobertos.

### Coleta pública complementar — 13/10/2026, 21:56

Continuei a busca TRF6 até a página 381. O portal mudou o total informado de
7.611 para 7.619 resultados durante a paginação; a validação interrompeu o lote
na página 381 depois de preservar 29 documentos. O avanço após o snapshot das
21:31 foi de 528 documentos TRF6. Não retentei o item que falhou por layout nem
o que sofreu timeout; a instabilidade do total fica registrada para retomada.

No TRF4, a busca `BPC` nas origens TRU4 e Turmas Recursais acrescentou 150
documentos (50 em cada lote concluído; 26.055 resultados informados pelo portal).
No TRF2, `benefício assistencial` acrescentou 109 documentos em lotes
concluídos, com cobertura até a página 66 de 2.228 informadas. Uma busca TRF2
adicional por `BPC`, incluindo TRF2, TRU2 e Turmas Recursais, falhou em um
resultado sem vínculo CNJ consistente após preservar 37 documentos. No TRF5,
uma busca por `benefício assistencial` parou em documento com seções publicadas
não reconhecidas. Na TNU, a consulta `BPC` encontrou outro artigo sem identidade
estável/CNJ e foi encerrada sem contorno. Essas falhas são específicas dos itens
ou consultas citados; outras consultas públicas podem ser tentadas.

Snapshot validado: 31.597 `documentos_publicos`, 16.737 processos e 813
vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
766; arquivo TRF1 7; TRF2 516; TRF4 767; TRF5 1.320; TRF6 8.672.
`PRAGMA quick_check=ok`; `foreign_key_check` sem violações. Backup:
`data/backup-pos-coleta-publica-20261013-2156.sqlite`, 1.184.210.944 bytes,
SHA-256 `D699BCEF7FBB828CE416F785E64186BBAB2B91E6DFFBBDE28BE7B28764E8FE6D`.
Próxima retomada recomendada: TRF2 `benefício assistencial` depois da página 66
ou TRF4 `BPC` após pular as URLs concluídas; TRF6 deve reiniciar pela página
381 e revalidar o total antes de avançar.

### Continuação TRF2/TRF4 — 13/10/2026, 22:03

Na sequência, mais dois lotes concluídos de `benefício assistencial` no TRF2
acrescentaram 56 documentos e avançaram a cobertura informada até a página 76
(de 2.228). No TRF4, mais um lote idempotente da busca `BPC` nas origens TRU4 e
Turmas Recursais acrescentou 50 documentos. O snapshot das 21:56 foi atualizado;
as buscas continuam abertas e podem ser retomadas pulando URLs já concluídas.

Snapshot validado: 31.703 `documentos_publicos`, 16.737 processos e 813
vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
766; arquivo TRF1 7; TRF2 572; TRF4 817; TRF5 1.320; TRF6 8.672.
`PRAGMA quick_check=ok`; `foreign_key_check` sem violações. Backup:
`data/backup-pos-coleta-publica-20261013-2203.sqlite`, 1.186.906.112 bytes,
SHA-256 `0766DE88858065743B7FA3AB4B1C82F01A50ABB475661F616EC5311129C2D620`.
Próxima retomada: TRF2 pela página 76 e TRF4 repetindo a consulta `BPC` com as
origens TRU4/Turmas Recursais; TRF6 pela página 381 após conferir o total atual.

### Continuação TRF2/TRF4/TRF6 — 13/10/2026, 22:27

Desde o snapshot das 22:03, o TRF2 acrescentou 110 documentos na consulta
`benefício assistencial`; a última rodada chegou à página 93 de 2.228. O TRF4
acrescentou outros 250 documentos na consulta `BPC`, origens TRU4 e Turmas
Recursais; a última rodada chegou à página 46 de 2.606. Ambas seguem aptas a
retomada idempotente.

O TRF6 foi retomado após a atualização do índice, cuja busca passou a informar
7.717 resultados. Lotes concluídos avançaram até a página 424 e acrescentaram
300 documentos. Um documento nessa página falhou porque o layout do inteiro
teor não foi reconhecido; a execução parou depois de preservar 15 documentos
do lote. O próximo passo é retomar na página 424, pulando URLs concluídas e o
item falho, sem contorná-lo.

Snapshot validado: 32.378 `documentos_publicos`, 16.737 processos e 820
vínculos explícitos. Por fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU
766; arquivo TRF1 7; TRF2 682; TRF4 1.067; TRF5 1.320; TRF6 8.987.
`PRAGMA quick_check=ok`; `foreign_key_check` sem violações. Backup:
`data/backup-pos-coleta-publica-20261013-2227.sqlite`, 1.205.719.040 bytes,
SHA-256 `C1A8780589E3863F8BE60D46AA4D09D2425819446B8A1BF825F07DB9B4F189CD`.

### Retomada TRF2 e checkpoint — 14/10/2026, 19:39

Retomei a consulta pública `benefício assistencial` do TRF2. A varredura
idempotente encontrou 55 documentos novos até a página 100. Como o comando
original não aceitava página inicial, acrescentei `--pagina-inicial`, mantendo
validação do documento, CNJ e formulário público; os cinco testes do coletor
TRF2 passaram. Com retomadas diretas nas páginas 101–132, entraram mais 153
documentos. Total desta sequência: **208 novos**, elevando TRF2 de 682 para 890.
O total informado pelo portal é 2.228 páginas; a busca segue incompleta.

Não houve criação de processos ou vínculos presumidos, alteração do contrato de
dados ou envio à IpeaIA. A fonte retornou alguns resultados sem texto BPC
elegível; foram preservados como respostas sem documento, sem inferir que não
existam autos do processo.

Snapshot validado: 32.786 `documentos_publicos`, 16.737 processos, 16.796 hits
DataJud, 907.521 movimentos, 827 vínculos documentais e zero extrações IA. Por
fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU 766; arquivo TRF1 7; TRF2
890; TRF4 1.067; TRF5 1.320; TRF6 9.187. `PRAGMA quick_check=ok` e
`foreign_key_check` sem violações. Backup:
`data/backup-pos-coleta-publica-20261014-1937.sqlite`, 1.216.774.144 bytes,
SHA-256 `82749D02523FAAA082AFB1D296C361277A2BA6C421EC91BD41E58D74C8688745`.
Próxima retomada TRF2: página 133. Próximo alvo: continuar TRF4 `BPC` em
TRU4/Turmas Recursais, com retomada de página se necessário.

### Retomada TRF4 e checkpoint — 14/10/2026, 20:00

Continuei a busca `BPC` nas origens públicas TRU4 e Turmas Recursais, retomando
pela página 47 e avançando até a página 157. Foram 16 lotes, totalizando **798
documentos novos**; o corpus TRF4 passou de 1.067 para 1.865. Os lotes validaram
o CNJ do card contra o documento, pularam URLs concluídas e não criaram processos
nem vínculos presumidos.

Para permitir retomada além do primeiro bloco de 100 páginas, acrescentei
`--pagina-inicial` também ao coletor TRF4, seguindo o padrão validado no TRF2.
Os testes combinados dos coletores TRF2/TRF4 passaram: 9 testes. Coletas
permanecem exclusivamente locais; sem envio à IpeaIA e sem alteração de schema.

Snapshot validado: 33.584 `documentos_publicos`, 16.737 processos, 16.796 hits
DataJud, 907.521 movimentos, 827 vínculos documentais e zero extrações IA. Por
fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU 766; arquivo TRF1 7; TRF2
890; TRF4 1.865; TRF5 1.320; TRF6 9.187. `PRAGMA quick_check=ok` e
`foreign_key_check` sem violações. Backup:
`data/backup-pos-coleta-publica-20261014-1958.sqlite`, 1.245.908.992 bytes,
SHA-256 `5DD11BB8BEB5F8E4F34D5F19DDF43AB57CCA15FB1C20704C276588CA03F2B5B9`.
Próxima página TRF4: 158. TRF2 está pronta para retomar da página 133.

### Continuação TRF4 e novo snapshot — 14/10/2026, 20:04

Mais dois lotes de `BPC` em TRU4/Turmas Recursais coletaram 100 documentos
adicionais, chegando à página 168. O total TRF4 passou de 1.865 para 1.965;
busca pública segue respondendo sem autenticação e sem falhas de layout neste
trecho. Próxima página TRF4: 169.

Snapshot validado: 33.684 `documentos_publicos`, 16.737 processos, 16.796 hits
DataJud, 907.521 movimentos, 827 vínculos documentais e zero extrações IA. Por
fonte: CJF/TRF1 18.535; PJe/TRF1 601; STJ 413; TNU 766; arquivo TRF1 7; TRF2
890; TRF4 1.965; TRF5 1.320; TRF6 9.187. `PRAGMA quick_check=ok`, sem violações
de chave estrangeira. Backup:
`data/backup-pos-coleta-publica-20261014-2003.sqlite`, 1.249.910.784 bytes,
SHA-256 `A5A048060BC93392E7708DDEBF287BB5796087D5806BC700B7B041826C326192`.

### Continuação de fontes públicas e medição de cobertura — 14/10/2026, 20:32

Retomadas concluídas sem autenticação, alteração de schema ou envio à IpeaIA:

- **TRF2 — “benefício assistencial”:** páginas 133–168, 300 URLs consultadas,
  **203 versões novas**. O total passou de 890 para 1.093; próxima página: 169.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 169–198, 227 documentos
  novos, com URLs já concluídas puladas. Total: 2.192; próxima página: 199.
- **TRF6 — “benefício de prestação continuada”:** retomada até a página 492;
  foram acrescentadas **24 versões** desde a contagem anterior, levando o total
  de 9.187 para 9.211. Lotes atravessaram trechos já concluídos, sem duplicar.
  Uma busca separada por “BPC” recebeu timeout de rede; não houve contorno.
- **STJ — arquivos JSON recentes das duas Turmas:** 24 recursos verificados;
  **12 versões novas** após deduplicação. Total: 425 documentos.
- **PJe/TRF1 — consulta pública por CNJ da amostra:** três processos foram
  consultados antes da interrupção por divergência de identidade no cabeçalho.
  Dois documentos passaram pela validação e foram gravados com vínculo CNJ
  explícito; um processo retornou sem documento disponível. O documento com
  identidade divergente não foi gravado; arquivos brutos foram preservados.
- **CJF por CNJ:** lote planejado de 50 interrompido por HTTP 504 na página
  pública; resultados anteriores foram preservados. Consultas vazias não são
  evidência de inexistência de autos.
- **TNU:** consulta “benefício assistencial” percorreu páginas até encontrar,
  na página 51, documento sem identidade estável no cabeçalho; coleta encerrada,
  sem gravar o item inválido. As URLs concluídas foram puladas.
- **TRF5:** busca “BPC” encontrou 126 URLs já concluídas; “LOAS” percorreu
  1.000 URLs concluídas; nenhuma versão nova nesta rodada.

Contagem final conferida: 34.152 `documentos_publicos`, 16.737 processos,
16.796 registros DataJud, 907.521 movimentos, 829 vínculos documentais e zero
extrações IA. Por fonte: CJF/TRF1 18.535; PJe/TRF1 603; STJ 425; TNU 766;
arquivo TRF1 7; TRF2 1.093; TRF4 2.192; TRF5 1.320; TRF6 9.211.
`PRAGMA quick_check=ok`, sem violações FK. Snapshot:
`data/backup-coleta-fontes-publicas-20261014-2029.sqlite` (1.264.623.616 bytes;
SHA-256 `6FC94E3637A267A6DC98098BBA66D5A499BADCCFFB1BDB639344505E07005D18`).

Próximas retomadas com melhor rendimento: TRF2 pela página 169, TRF4 pela 199
e testar termos alternativos nos portais que seguem respondendo. TRF6 alternativa
por “BPC” aguarda condição de rede melhor; PJe/CJF/TNU não devem repetir o item
que falhou em validação/timeout. CRPS continua dependente de consulta manual
autenticada pelo pesquisador.

### Nova retomada TRF2/TRF4 e snapshot — 14/10/2026, 20:40

Após o checkpoint anterior, as buscas públicas seguiram sem autenticação e sem
falhas nos dois portais:

- TRF2, consulta “benefício assistencial”: páginas 169–186, 300 URLs consultadas
  em seis lotes; **77 versões novas**. Total TRF2: 1.170; próxima página: 187.
- TRF4, consulta “BPC” nas origens TRU4/Turmas Recursais: páginas 199–216;
  **140 versões novas**. O último lote pulou 12 URLs concluídas e consultou 41;
  total TRF4: 2.332; próxima página: 217.

Total acumulado desde o snapshot anterior: **217 documentos novos**, sem criar
processos ou vínculos presumidos e sem enviar texto à IpeaIA. A base contém agora
34.369 `documentos_publicos`, 16.737 processos, 16.796 registros DataJud,
907.521 movimentos, 829 vínculos e zero extrações IA. Por fonte: CJF/TRF1
18.535; PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 1.170; TRF4
2.332; TRF5 1.320; TRF6 9.211. `PRAGMA quick_check=ok` e sem violações FK.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2038.sqlite`,
1.271.869.440 bytes, SHA-256
`5E47A75D5DB7365D18E770553568B907CFB3D1683AFCCDA3EC18C47068350AA0`.
Retomar TRF2 da página 187 e TRF4 da 217. TRF6/consulta alternativa “BPC”
segue aguardando condição de rede; o erro de identidade no PJe, HTTP 504 no CJF
e identidade ausente na TNU não serão repetidos neste ambiente.

### Continuação TRF2/TRF4 e snapshot — 14/10/2026, 20:46

Desde o checkpoint das 20:40, as consultas públicas acrescentaram **168
documentos**:

- TRF2 “benefício assistencial”: páginas 187–198, 100 URLs consultadas em dois
  lotes; **68 versões novas**. Total: 1.238; próxima página: 199.
- TRF4 “BPC”, TRU4/Turmas Recursais: páginas 217–228; **100 versões novas**.
  Dois lotes consultaram 50 URLs cada e pularam URLs já concluídas. Total: 2.432;
  próxima página: 229.

Sem processos novos, vínculos presumidos, alteração de schema ou envio à IpeaIA.
Base conferida: 34.537 `documentos_publicos`, 16.737 processos, 16.796 registros
DataJud, 907.521 movimentos, 829 vínculos e zero extrações IA. Por fonte:
CJF/TRF1 18.535; PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 1.238;
TRF4 2.432; TRF5 1.320; TRF6 9.211. `PRAGMA quick_check=ok`, sem violações FK.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2045.sqlite`,
1.277.411.328 bytes, SHA-256
`D04299A9E28CE91EBF9AC0302FBCFCBBC77EC2FD10ADC3754432488EB6202E17`.
Próxima retomada: TRF2 página 199, TRF4 página 229. As tentativas de continuar
no TRF6 seguem suspensas diante do timeout; as rotas CJF/TNU/PJe não repetirão
itens que falharam em disponibilidade ou validação.

### Continuação TRF2/TRF4 e snapshot — 14/10/2026, 20:55

Retomadas públicas sem credenciais, após o checkpoint das 20:46:

- **TRF2 — “benefício assistencial”:** páginas 199–215, em três lotes de até
  50 URLs. Foram consultadas 145 URLs e incorporadas **90 versões novas**; o
  total da fonte passou de 1.238 para **1.328**. A página 215 deve ser retomada
  para assegurar cobertura dos links restantes; URLs concluídas são puladas.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 229–245 em três lotes;
  **135 versões novas**, elevando a fonte de 2.432 para **2.567**. Próxima
  a página 245 deve ser retomada para assegurar cobertura dos links restantes;
  URLs concluídas são puladas.

No total, entraram **225 documentos/versões**. Não foram criados processos nem
vínculos presumidos; nenhum conteúdo foi enviado à IpeaIA. A base ficou com
34.762 `documentos_publicos`, 16.737 processos, 16.796 registros DataJud,
907.521 movimentos, 829 vínculos e zero extrações IA. Por fonte: CJF/TRF1
18.535; PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 1.328; TRF4
2.567; TRF5 1.320; TRF6 9.211. `PRAGMA quick_check=ok` e
`foreign_key_check` sem violações.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2055.sqlite`,
1.283.137.536 bytes, SHA-256
`16AF664F7209F634E1751220772C6376DF6C4F102B6AF778F10FABA0DBEFF54F`.
TRF2 e TRF4 continuam sendo as fontes públicas com melhor rendimento nesta
retomada. TRF6/BPC aguarda condição de rede; as falhas anteriores de identidade
no PJe/TNU e HTTP 504 no CJF não foram repetidas.

### Continuação TRF2/TRF4 e snapshot — 14/10/2026, 21:13

As retomadas públicas acrescentaram **588 documentos/versões** desde o
checkpoint das 20:55:

- **TRF2 — “benefício assistencial”:** retomada da página 215 até a 254,
  distribuída em oito lotes idempotentes; **244 versões novas** desde o
  checkpoint. O total da fonte passou de 1.328 para **1.572**. Retomar na
  página 255, pulando URLs concluídas.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** retomada da página 245 até a 284,
  em oito lotes; **344 versões novas**. O total passou de 2.567 para **2.911**.
  Retomar na página 285, pulando URLs concluídas.

Não foram criados processos, vínculos presumidos ou extrações IA. Estado
conferido: 35.350 `documentos_publicos`, 16.737 processos, 16.796 registros
DataJud, 907.521 movimentos, 829 vínculos e zero extrações IA. Por fonte:
CJF/TRF1 18.535; PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 1.572;
TRF4 2.911; TRF5 1.320; TRF6 9.211. `PRAGMA quick_check=ok` e
`foreign_key_check` sem violações.

Snapshot: `data/backup-coleta-fontes-publicas-20261014-2113.sqlite`,
1.302.663.168 bytes, SHA-256
`EC235D444AC1CE807426DC59E514E45673C6E091502C5C6ABA55045C6EC1EB86`;
integridade conferida no próprio snapshot. TRF2 e TRF4 seguem respondendo sem
autenticação. As coletas são de corpus jurisprudencial público, não de novos
processos da amostra DF/RIDE.

### Retomadas TRF2/TRF4 e testes adicionais — 14/10/2026, 21:23

Desde o snapshot das 21:13, foram acrescentadas **181 versões**:

- **TRF2 — “benefício assistencial”:** páginas 255–264 em dois lotes, **63
  versões novas**. Total da fonte: **1.635**; retomar na página 265.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 285–294 em dois lotes, **87
  versões novas**. Total: **2.998**; retomar na página 295.
- **TRF5 — “benefício de prestação continuada”:** consulta alternativa pública
  incorporou **24 versões** antes do documento 12 apresentar seções não
  reconhecidas; o lote parou preservando os anteriores. Na consulta “amparo
  social”, entraram **7 versões** antes de surgir linha sem link único de
  documento. Não repetir os itens inválidos.
- **TNU — “benefício de prestação continuada”:** as primeiras 100 URLs estavam
  concluídas, sem novas versões.
- **TRF3:** o buscador oficial localizou documentos pertinentes, mas o teste do
  coletor em duas URLs diretas expirou no primeiro documento. Nenhum arquivo
  TRF3 foi gravado; não repetir enquanto o acesso direto continuar expirando.

Contagem conferida: **35.531 `documentos_publicos`**, 16.737 processos, 16.796
registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações,
829 vínculos e zero extrações IA. Por fonte: CJF/TRF1 18.535; PJe/TRF1 603;
STJ 425; TNU 766; arquivo TRF1 7; TRF2 1.635; TRF4 2.998; TRF5 1.351;
TRF6 9.211. `PRAGMA quick_check=ok`; sem violações em `foreign_key_check`.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2123.sqlite`,
1.308.205.056 bytes, SHA-256
`553B79D120600D07E7BE36CE0FDCFAE19312A3979E5C727642E45EFD431DB193`.
Próximas retomadas com rendimento: TRF2 página 265 e TRF4 página 295. TRF5
fica em pausa nos layouts/links inválidos; TNU não tinha itens novos no recorte
consultado; TRF3 depende de o acesso direto voltar a responder.

### Retomada TRF2/TRF4 e snapshot — 14/10/2026, 21:32

Desde o checkpoint das 21:23, TRF2 e TRF4 acrescentaram **277 versões** em
quatro lotes por fonte:

- **TRF2 — “benefício assistencial”:** páginas 265–284, **110 versões novas**;
  total da fonte: **1.745**. Retomar na página 285.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 295–314, **167 versões
  novas**; total: **3.165**. Retomar na página 315.

Contagem: **35.808 `documentos_publicos`**, 16.737 processos, 16.796 registros
DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações, 829
vínculos e zero extrações IpeaIA. Por fonte: CJF/TRF1 18.535; PJe/TRF1 603;
STJ 425; TNU 766; arquivo TRF1 7; TRF2 1.745; TRF4 3.165; TRF5 1.351;
TRF6 9.211. `PRAGMA quick_check=ok`; `foreign_key_check` sem violações.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2132.sqlite`,
1.316.810.752 bytes, SHA-256
`6A7602FA2E6AD482AB8FE2ADC8ABECEEAA1F6AE56BBBC7772F8D7C9D07A7B880`.
A coleta das fontes sem credenciais permanece em andamento; TRF3/TRF5/TNU
mantêm as barreiras documentadas no checkpoint de 21:23.

### Retomada TRF2/TRF4 e snapshot — 14/10/2026, 21:45

Desde o checkpoint das 21:32, os lotes públicos acrescentaram **440 versões**:

- **TRF2 — “benefício assistencial”:** páginas 285–314; **163 versões novas**
  desde o checkpoint (98 delas nas páginas 295–314). Total da fonte: **1.908**.
  Próxima página: 315.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 315–332 e 334–348; **277
  versões novas** desde o checkpoint (184 delas nas páginas 325–332 e 334–348).
  Total da fonte: **3.442**. Na página 333 o coletor encontrou
  um layout de documento não reconhecido e preservou o lote anterior; o item
  problemático foi pulado e a coleta foi retomada na página 334. Próxima página:
  349.

Estado conferido no banco: **36.248 `documentos_publicos`**, 16.737 processos,
16.796 registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302
comunicações, 829 vínculos documentais e zero extrações IpeaIA. Por fonte:
CJF/TRF1 18.535; PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 1.908;
TRF4 3.442; TRF5 1.351; TRF6 9.211. `PRAGMA quick_check=ok` e
`foreign_key_check` sem violações. Não foram criados processos nem vínculos
presumidos; nenhum documento foi enviado à IpeaIA.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2145.sqlite`,
1.333.141.504 bytes, SHA-256
`A0F5762648FF4EDD25FCA81CA6CABED47DB840E3F4F6EA1EB8256BFC32B1714F`;
integridade, vínculos e contagem de documentos conferidos no próprio snapshot.
TRF2/TRF4 seguem sendo as fontes públicas sem autenticação que estão rendendo
nesta retomada. CRPS permanece dependente de consulta do pesquisador; TRF3/TRF5,
TNU e TRF6 continuam com as barreiras registradas nos checkpoints anteriores.

### Continuação TRF2/TRF4 e snapshot — 14/10/2026, 21:55

Desde o snapshot das 21:45, foram acrescentadas **325 versões**:

- **TRF2 — “benefício assistencial”:** retomada das páginas 315–340; **153
  versões novas**. O total passou de 1.908 para **2.061**. Dois documentos
  apresentaram layout não reconhecido (páginas 324 e 335); os itens foram
  pulados e a coleta continuou, sem perda dos documentos anteriores. Retomar
  na página 341.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 349–368; **172 versões
  novas**. O total passou de 3.442 para **3.614**. Próxima página: 369.

Contagem conferida: **36.573 `documentos_publicos`**, 16.737 processos, 16.796
registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações,
829 vínculos documentais e zero extrações IpeaIA. Por fonte: CJF/TRF1 18.535;
PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 2.061; TRF4 3.614;
TRF5 1.351; TRF6 9.211. `PRAGMA quick_check=ok` e `foreign_key_check` sem
violações. Nenhum processo ou vínculo presumido foi criado; sem envio à IpeaIA.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2155.sqlite`,
1.346.375.680 bytes, SHA-256
`5D6C98EF24E664A244277C4293C9EAD21C19145F2C1ECC1A737F154FB64418CB`;
integridade e contagem de documentos conferidas no próprio arquivo.

### Consultas temáticas alternativas TRF2/TRF4 e snapshot — 14/10/2026, 21:58

As tentativas de diversificar os termos de busca acrescentaram **35 versões**
desde o snapshot das 21:55, todas no TRF4:

- **TRF4 — “LOAS”:** páginas 1–9; **21 versões novas**. Próxima página: 10.
- **TRF4 — “benefício assistencial”:** páginas 1–7; **13 versões novas**.
  Próxima página: 8.
- **TRF4 — “amparo social”:** páginas 1–2; **1 versão nova**. Próxima página: 3.
- **TRF2 — “BPC”, “LOAS” e “benefício assistencial ao idoso”:** primeiras duas
  páginas de cada busca não acrescentaram documentos; os 60 links já estavam
  concluídos no banco. Não repetir essas páginas.

Estado atual: **36.608 `documentos_publicos`**, 16.737 processos, 16.796
registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações,
829 vínculos e zero extrações IpeaIA. Por fonte: CJF/TRF1 18.535; PJe/TRF1
603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 2.061; TRF4 3.649; TRF5 1.351;
TRF6 9.211. `PRAGMA quick_check=ok`; `foreign_key_check` sem violações.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2158.sqlite`,
1.347.813.376 bytes, SHA-256
`967D4715C1A84C99C510B97038EF07BF4461A900062DEE91AE0C63DA5D47876A`;
contagem e integridade conferidas no próprio snapshot. As buscas principais
seguem com rendimento; retomar TRF2 “benefício assistencial” na página 341,
TRF4 “BPC” na 369, “LOAS” na 10 e “benefício assistencial” na 8. CRPS continua
dependente do pesquisador; não se usaram credenciais nem controles foram
contornados.

### Retomada TRF2/TRF4 e snapshot — 14/10/2026, 22:15

Desde o checkpoint das 21:58, as buscas principais acrescentaram **551
versões**:

- **TRF2 — “benefício assistencial”:** páginas 341–380; **225 versões novas**.
  Total da fonte: **2.286**. Próxima página: 381.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 369–408; **326 versões
  novas**. Total da fonte: **3.975**. Próxima página: 409.

Conferência atual: **37.159 `documentos_publicos`**, 16.737 processos, 16.796
registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações,
829 vínculos documentais e zero extrações IpeaIA. Por fonte: CJF/TRF1 18.535;
PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 2.286; TRF4 3.975;
TRF5 1.351; TRF6 9.211. `PRAGMA quick_check=ok`; sem violações em
`foreign_key_check`. Nenhum processo/vínculo foi presumido e nada foi enviado
à IpeaIA.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2215.sqlite`,
1.363.161.088 bytes, SHA-256
`55D1257A19C713BF50EFC9C7F903F2395ADFC021DF3AC3F96D66A9ADB466BFB6`;
integridade, vínculos e contagem conferidos no próprio arquivo. Consultas
alternativas do TRF4 também renderam: “LOAS” +21, “benefício assistencial” +13
e “amparo social” +1; TRF2 “BPC”, “LOAS” e “benefício assistencial ao idoso”
não acrescentaram itens nas primeiras duas páginas. As páginas com layouts não
reconhecidos nas consultas anteriores foram puladas e a coleta prosseguiu.

### Continuação da coleta TRF2/TRF4 e snapshot — 14/10/2026, 22:31

Desde o checkpoint das 22:15, entraram **538 versões novas**:

- **TRF2 — “benefício assistencial”:** páginas 381–420; **212 versões novas**.
  Total da fonte: **2.498**. Próxima página: 421. As páginas 411–420 renderam
  apenas 31 versões; manter a consulta atual por enquanto, sem ampliar o lote.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 409–448; **326 versões
  novas**. Total: **4.301**. Próxima página: 449.

Banco conferido: **37.697 `documentos_publicos`**, 16.737 processos, 16.796
registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações,
829 vínculos documentais e zero extrações IpeaIA. Por fonte: CJF/TRF1 18.535;
PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 2.498; TRF4 4.301;
TRF5 1.351; TRF6 9.211. `PRAGMA quick_check=ok`; sem violações em
`foreign_key_check`. Nenhum processo/vínculo presumido foi criado; nada foi
enviado à IpeaIA.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2231.sqlite`,
1.384.697.856 bytes, SHA-256
`B69226F04647112412511BC8E5F040B6371CA60B69148CB7DFCDED831DC4B150`;
contagem, integridade e chaves estrangeiras conferidas no próprio snapshot.
As páginas com layouts não reconhecidos em lotes anteriores foram puladas, e a
coleta seguiu em páginas posteriores. Próximos lotes principais: TRF2 página
421; TRF4 página 449.

### Continuação das buscas principais e alternativas TRF4 — 14/10/2026, 22:45

Desde o checkpoint das 22:31, foram coletadas **264 versões novas**:

- **TRF2 — “benefício assistencial”:** páginas 421–435; **101 versões novas**.
  Total da fonte: **2.599**. Próxima página: 436.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 449–463; **127 versões
  novas**. Total da fonte após as buscas principais e alternativas: **4.464**.
  Próxima página da busca BPC: 464.
- **TRF4 — “LOAS”:** páginas 10–14; **26 versões novas**. Próxima página: 15.
- **TRF4 — “benefício assistencial”:** páginas 8–12; **8 versões novas**.
  Próxima página: 13.
- **TRF4 — “amparo social”:** páginas 3–7; **2 versões novas**. Próxima página: 8.

Nas buscas alternativas, muitos links foram pulados por já estarem concluídos e
deduplicados. As rotinas registraram os itens novos sem enviar conteúdo à IA e
sem criar vínculos presumidos com processos da amostra.

Banco conferido: **37.961 `documentos_publicos`**, 16.737 processos, 16.796
registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações,
829 vínculos documentais e zero extrações IpeaIA. Por fonte: CJF/TRF1 18.535;
PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2 2.599; TRF4 4.464;
TRF5 1.351; TRF6 9.211. `PRAGMA quick_check=ok`; `foreign_key_check` sem
violações.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261014-2245.sqlite`,
1.392.738.304 bytes, SHA-256
`94DA75E0F9D6E29A2B6D489724BB55A138BDDEDA860BA2DC194D4D7793463F09`;
conferido no próprio arquivo: 37.961 documentos/versões, `quick_check=ok` e
nenhuma violação de chave estrangeira. Próximas páginas: TRF2 principal 436;
TRF4 BPC 464, LOAS 15, benefício assistencial 13 e amparo social 8.

### Retomada de fontes públicas e atualização INSS — 15/10/2026, 19:14

Retomadas sem credenciais e com deduplicação por URL/documento:

- **TRF2 — “benefício assistencial”:** páginas 516–525 (+27 versões), 526
  interrompida por resultado sem links únicos de documento/processo, páginas
  527–531 (+19) e 532–536 (+14). A página 526 foi pulada; próxima: 537.
- **TRF4 — “BPC”, TRU4/Turmas Recursais:** páginas 547–551 (+38); retomada em
  552–555 (+26 preservadas antes de falha no layout, documento
  `711775766662818015642763916019` na página 555); páginas 556–560 (+48),
  561–565 (+38), 566–570 (+41), 571–575 (+47) e 576–580 (+39). Próxima: 581.
  Buscas alternativas: “LOAS”, páginas 15–19 (+0, 50 links já concluídos);
  “benefício assistencial”, páginas 13–17 (+11); “amparo social”, páginas
  8–12 (+8). Próximas páginas alternativas: 20, 18 e 13, respectivamente.
- **TRF6 — “BPC”, Turmas Recursais:** página 425 sem novos itens; páginas
  426–430 (+7), 431–435 (+4), 436–440 (+9), 441–445 (+30) e 446–450 (+49
  preservadas antes de falha no layout, documento
  `381770920126128211065497442305` na página 450). Pular a página parcial 450 e
  retomar na 451. O acesso voltou a responder sem credencial; os itens inválidos
  não impediram as coletas anteriores.
- **TRF5:** buscas “BPC” e “benefício assistencial”, cinco páginas/50 links cada;
  sem novos itens, pois todos já estavam concluídos. **TNU:** “benefício
  assistencial” e “LOAS”, igualmente 50 links concluídos por consulta e zero
  itens novos. Foram consultas sem autenticação e sem mudança na base.

Também atualizei **INSS concessões** para a competência 202609 nas UFs DF, GO e
MG: 105.751 linhas lidas, 1.889 registros BPC selecionados e 19 agregados novos
armazenados. O catálogo não tinha XLSX para a competência 202610. No dataset de
**indeferimentos**, o XLSX rotulado “SETEMBRO DE 2026” continha competência
202605 nas linhas; a validação rejeitou a importação. A resposta bruta foi
preservada em `data/raw` para auditoria, sem gravar agregados incorretos. O
Censo SUAS 2025 já estava completo nesta cópia (5.547 agregados de CRAS e 3.010
de Postos de Cadastramento); não foi baixado novamente.

Resultado conferido no banco consolidado: **39.515 `documentos_publicos`**,
16.737 processos, 16.796 registros DataJud, 907.521 movimentos, 1.241 consultas
PJe, 302 comunicações, 830 vínculos documentais e zero extrações IpeaIA. Por
fonte: CJF/TRF1 18.535; PJe/TRF1 603; STJ 425; TNU 766; arquivo TRF1 7; TRF2
3.048; TRF4 5.470; TRF5 1.351; TRF6 9.310. INSS: 467 agregados de
indeferimentos e 185 de concessões; Censo SUAS: 8.557 agregados. Nenhum lote
foi enviado à IpeaIA e não foram criados processos novos.

Snapshot validado: `data/backup-coleta-fontes-publicas-20261015-1913.sqlite`,
1.445.421.056 bytes, SHA-256
`93ADD99128D59EA90BDE480DE22AC18B2B3FC7202B100B92CA8089B075CC1BA8`;
conferido no próprio arquivo: 39.515 documentos/versões, `quick_check=ok` e
nenhuma violação de chave estrangeira. Próximas retomadas: TRF2 p. 537, TRF4 BPC
p. 581, TRF6 p. 451.

### Coleta direcionada aos processos do estudo — PJe público TRF1 — 15/10/2026

Por orientação do estudo, a coleta de jurisprudência geral de TRF2/TRF4/TRF6 foi
interrompida; o trabalho passou a consultar somente processos já existentes na
amostra DataJud do TRF1, em primeiro grau (`G1`/`JE`), assuntos CNJ 6114, 11946 e
11947, órgãos dos municípios DataJud 743 (Brasília), 1798 (Formosa) e 2788
(Luziânia). O universo elegível identificado é de **3.823 processos**. A consulta
pública oficial do PJe TRF1 não exigiu login nem chave.

Até este registro, **936 números de processo únicos de 3.823 candidatos** foram
consultados (24,5%): 827 consultas concluídas, 73 sem documentos listados e 36
com falha; houve 17 tentativas repetidas. A cobertura por município do órgão é
desigual: Brasília 258/1.793, Formosa 356/1.031 e Luziânia 322/999. Portanto, o
acervo é útil para exploração, mas não é amostra aleatória nem representativa.
As falhas de identidade de documento foram preservadas e não associadas ao
processo incorreto. Desde 15/10, entraram **1.678 documentos vinculados a 596
processos**. O acervo PJe direcionado soma agora **2.281 documentos em 843
processos**. Os documentos disponíveis são decisões (597), despachos (816),
sentenças (785), acórdãos (78) e decisões monocráticas terminativas (5). Nenhum
processo novo foi criado e nenhum conteúdo foi enviado à IpeaIA.

Triagem textual descritiva dos 2.281 documentos: 523 mencionam “LOAS”, 257
mencionam “BPC”, 374 mencionam “requerimento administrativo”, 110 mencionam
“indeferimento administrativo” e 394 mencionam “impedimento de longo prazo”. Os
termos se sobrepõem e são apenas indicadores de busca — não são classificação
jurídica nem evidência revisada caso a caso. Não foi encontrado documento
rotulado como petição inicial. Assim, os atos judiciais já podem ajudar a
recuperar fundamentos e contexto que a movimentação DataJud não traz, mas a
consulta pública ainda não entrega, de forma sistemática, o pedido inicial nem
o processo administrativo do INSS, que explicariam mais diretamente a origem
da judicialização.

Estado do banco consolidado após a coleta: **41.353 documentos públicos**, 16.737
processos, 16.796 registros DataJud, 907.521 movimentos e zero extrações IpeaIA.
Por ora, a prioridade permanece no TRF1 da amostra; as buscas gerais TRF2/TRF4/
TRF6 não devem ser retomadas nesta tarefa.
