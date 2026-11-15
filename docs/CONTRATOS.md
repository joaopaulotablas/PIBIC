# Contrato de dados BPC Jud — v0.10

Este documento substitui o contrato v0.1 baseado em SQLite/MongoDB.

## Fontes

- DataJud: universo de processos e movimentos dos assuntos 6114, 11946 e 11947;
- Comunica PJe: comunicações e atos publicados consultados por número CNJ;
- PJe/TRF1 consulta pública: documentos HTML explicitamente disponibilizados
  em `documentoSemLoginHTML.seam`, vinculados por CNJ e ID de documento conferidos;
- TPU local: nomes e hierarquias de assuntos, classes e movimentos do CNJ.
- CKAN/INSS: catálogo em `recursos_externos` e indeferimentos BPC agregados por
  competência, UF, espécie e motivo em `indicadores_inss_indeferimentos`.
- CJF/TRF1/JEF1, STJ, TNU, TRF2, TRF4, TRF5 e TRF6: corpus complementar em `documentos_publicos`; vínculos
  explícitos com a amostra em `documento_processos`, sem aumentar a população.
- TJMG: registros DataJud suplementares por assunto e órgão julgador; não presumir
  competência federal delegada nem residência no município do órgão.
- Portal da Transparência/CGU: `GET /api-de-dados/bpc-por-municipio`, indicadores
  mensais agregados de BPC por código IBGE, autenticados pelo cabeçalho
  `chave-api-dados`. O token vem do ambiente, nunca do código ou do payload.
- MDS/Censo SUAS: arquivos públicos anuais de unidades socioassistenciais,
  agregados por código IBGE em `indicadores_suas_municipio`; não são dados de
  requerentes BPC nem de processos.
- MDS/VIS DATA: tempo médio regional de concessão do BPC e série anual de
  beneficiários/valores por município pagador, ambos preservados localmente como
  contexto agregado; não são processos nem provam residência dos litigantes.
- IBGE/SIDRA: tabela 9514 do Censo 2022 (população por idade) para DF e
  municípios oficialmente listados na RIDE; respostas preservadas localmente,
  sem tabela Silver e sem vinculação a processos ou pessoas.
- IBGE/SIDRA: tabelas 10131 (deficiência por grupo etário) e 10295 (rendimento
  domiciliar per capita) do Censo 2022, coletadas para os mesmos 34 municípios
  da RIDE; dados locais agregados, sem integração à Silver.

## Identidades

- Entidade processo: `processos.numero_processo`, CNJ formatado e único;
- Hit DataJud: par `registros_datajud.datajud_index + datajud_id`;
- Comunicação: par `processo_id + hash_conteudo`;
- Hit e processo não são sinônimos: um processo pode possuir mais de um registro
  por grau, índice ou atualização.

## Camadas

### Bronze

Comunica (correção de 08/10/2026): cada resposta é um membro gzip completo.
O coletor copia o arquivo anterior para temporário no mesmo diretório, acrescenta
o membro, sincroniza os bytes e publica por substituição atômica antes da Silver.
Formato continua NDJSON gzip e caminho da coleta permanece igual. Interrupção
durante a próxima escrita não altera o último arquivo canônico completo; pode
deixar temporário `.partial`, que não é uma resposta publicada. O modo é restrito
ao Comunica porque copiar o arquivo a cada resposta tem custo crescente; usar
lotes pequenos. Arquivos históricos truncados não são reparados nem sobrescritos.
Ctrl+C encerra status `falhou`; encerramento forçado do processo não pode garantir
atualização do status no banco, embora preserve a última Bronze publicada.
Três falhas temporárias consecutivas ou um bloqueio encerram o lote, sem converter
erro em vazio; retentativas internas por CNJ continuam limitadas.

Respostas imutáveis em `data/raw/<fonte>/<particao>/<data>/<execucao>.ndjson.gz`.
O conteúdo deve permanecer igual ao recebido.

### Silver

PostgreSQL normalizado:

- `coletas`;
- `tarefas_painel`;
- `processos`;
- `registros_datajud`;
- `assuntos` e `registro_assuntos`;
- `movimentos`;
- `consultas_pje`;
- `comunicacoes_pje`;
- `referencias_tpu`;
- `documento_chunks`;
- `extracoes_ia`.
- `recursos_externos` (catálogo de fontes, não indicadores importados).
- `indicadores_bpc_municipio` (agregados da CGU; não são processos).
- `documentos_publicos`, `documento_processos` (corpus complementar e vínculos).
- `indicadores_inss_indeferimentos` (agregados administrativos, não processos).
- `indicadores_inss_concessoes` (agregados de concessão por despacho, não processos).
- `indicadores_suas_municipio` (Censo SUAS: contagens anuais de unidades
  socioassistenciais por município, sem relação individual com processos ou
  beneficiários).

O payload bruto também fica em JSONB, mas os campos usados em filtros e junções
devem possuir colunas tipadas.

#### Variação real de `assuntos` no DataJud (07/10/2026)

Um hit real do TRF1/G1 (vara de Goiânia) retornou `assuntos` como lista
aninhada: `[[{"codigo":11946,"nome":"Deficiente"}],{"codigo":15516}]`.
Bronze e `registros_datajud.payload` preservam o objeto recebido sem alteração.
Na projeção normalizada, listas internas são achatadas recursivamente para a
lista canônica de objetos `{codigo, nome}`; códigos sem nome permanecem com
`nome: null` até eventual enriquecimento TPU. Não se infere nem se descarta o
código. Isso não cria tabela nem altera o schema Silver; apenas torna o parser
compatível com a variação observada. O bruto fica disponível para auditoria.

### Contrato de `indicadores_bpc_municipio`

Um registro por `fonte + mes_ano + codigo_ibge + tipo_id`:

| Campo | Tipo | Significado |
| --- | --- | --- |
| `fonte` | `varchar(30)` | `portal_transparencia` |
| `mes_ano` | `integer` | Competência `AAAAMM` pedida na API |
| `data_referencia` | `date` | Data retornada pela API |
| `codigo_ibge` | `varchar(7)` | Município do indicador, não do órgão julgador |
| `municipio_nome`, `uf` | `text`, `varchar(2)` | Rótulos retornados pela API |
| `tipo_id` | `integer` | Identificador do tipo BPC retornado |
| `quantidade_beneficiados` | `bigint` | Estoque de beneficiados informado no mês |
| `valor` | `numeric(18,2)` | Valor monetário nominal informado no mês |
| `payload` | `jsonb` | Objeto original da API, sem token |
| `coleta_id`, `coletado_em` | `uuid`, `timestamptz` | Última coleta que confirmou o indicador |

As páginas completas da API, inclusive respostas vazias, ficam na Bronze sob
`data/raw/transparencia_bpc/municipios/`. Uma repetição atualiza a mesma chave
sem duplicar. O indicador não pode ser unido diretamente a uma pessoa ou ação
judicial; município do indicador e município do órgão julgador são conceitos
distintos. Não usar a quantidade como denominador de taxa de procedência.

### Gold

As views iniciais são:

- `vw_resumo_tribunais`;
- `vw_processos_analiticos`;
- `vw_cobertura_comunica`.

Novas métricas devem registrar fórmula, população, tratamento de ausências e
versão da pipeline.

## Consolidação local de origens — 07/10/2026

A união é produzida em um SQLite novo, com `Base.metadata` da aplicação; os
bancos de origem são somente leitura. O arquivo `bpc-jud.sqlite.gz` em
`transferencia/` é descompactado antes da leitura. Snapshots PostgreSQL devem
ser exportados primeiro com `portable.copy_database`/`scripts/snapshot_database.py`.
`SqliteStore`/`processos_raw` não participam desta união.

Identidades de processo, DataJud, comunicação, documento, extração, indicador
e associações usam as chaves lógicas descritas acima. IDs numéricos locais são
remapeados e toda FK usa o mapa da origem; UUIDs de coleta/tarefa são mantidos
quando livres. Para entidades sem chave de versão, conteúdo idêntico é contado
como duplicata e conteúdo divergente na mesma identidade vira conflito
explícito, com origem anterior e origem concorrente no relatório JSON. Mantém-se
uma linha Silver por chave única; conflitos mutáveis não são mesclados por
heurística nem sobrescritos silenciosamente. Documentos com hash diferente
continuam versões distintas. Indicadores mensais com a mesma chave não são
somados; divergências são relatadas como conflito.

Na consolidação, `extracoes_ia` é processada depois dos registros DataJud.
Referências `resultado.evidencias[].registro_id` são remapeadas pelo mapa da
mesma origem e devem pertencer ao processo da extração no destino. ID ausente
no mapa, não inteiro ou de outro processo rejeita a consolidação, inclusive
no dry-run; nunca se usa coincidência de ID local como fallback. O relatório
registra origem, PK da extração, posição da evidência e IDs original/destino.
Texto, classificação, versão do prompt e demais campos não mudam; as origens
preservam o resultado original. A comparação lógica de consolidações também
normaliza essas referências pela identidade DataJud, não pelo ID numérico.

Uma origem indisponível deve ser marcada fora do banco e não simulada. Referências
Bronze são copiadas como texto, sem alegar que o arquivo existe. Um caminho
ausente permanece indisponível e é enumerado no relatório da execução. A
consolidação não promove automaticamente o SQLite novo à base do pesquisador.

## Complementação pública — contrato v0.6 (06/10/2026)

As novas fontes NÃO ampliam silenciosamente a população de processos DataJud.
STJ e jurisprudência CJF/TRF1/JEF formam corpus complementar identificado por
fonte. Um documento só é vinculado a um processo existente quando há CNJ
completo explicitamente informado em campo estruturado da origem. Não ligar por
nome, número curto do STJ, similaridade de texto ou hipótese de recurso.

### `documentos_publicos`

| Campo | Tipo lógico | Regra |
| --- | --- | --- |
| `id` | bigint PK autogerado | Identificador local |
| `fonte` | varchar(30) | `stj`, `cjf_trf1`, `trf1_arquivo`, `tnu`, `pje_trf1`, `trf2_jurisprudencia`, `trf3_jurisprudencia`, `trf4_jurisprudencia`, `trf5_jurisprudencia`, `trf6_jurisprudencia` |
| `documento_id` | varchar(200) | ID estável da origem, nunca posição de página |
| `hash_conteudo` | varchar(64) | SHA-256 do JSON normalizado do documento |
| `tipo_documento`, `tribunal` | varchar(100), varchar(30) | Tipo e órgão, quando informados |
| `numero_origem` | text | Número como consta da fonte; pode não ser CNJ |
| `numeros_cnj` | JSON/JSONB lista | CNJs completos estruturados, sem extração de nomes |
| `data_publicacao`, `data_decisao` | date, nullable | Só data parseável explícita |
| `ementa`, `decisao`, `texto` | text, nullable | Conteúdo publicado; não implica autos completos |
| `url_origem` | text | Página oficial de referência |
| `recurso_url`, `arquivo_bruto` | text | Recurso oficial e caminho Bronze local |
| `payload` | JSON/JSONB objeto | Campos originais do documento, sem credenciais |
| `coleta_id` | UUID FK `coletas` | Execução que observou a versão |
| `coletado_em` | timestamp UTC | Momento da coleta |

Chave única: `fonte + documento_id + hash_conteudo`. Repetições não duplicam;
alteração gera nova versão, sem reescrever o documento antigo. Os vínculos em
`documento_processos` usam PK composta `documento_id` (FK documentos_publicos.id)
+ `processo_id` (FK processos.id), com `criterio` varchar(40) igual a
`cnj_explicito`. O vínculo indica identidade, não valida concessão inicial.

O coletor STJ pode incluir o histórico ZIP por opção explícita `--historico`.
Preserva o ZIP original antes de interpretar seus membros JSON, sem extrair
arquivos no sistema de arquivos. Aceita apenas listas de objetos, como nos
recursos JSON mensais; nomes de membros não são usados como caminhos locais.
Impõe limites de tamanho comprimido, expandido e por membro, e rejeita ZIP
criptografado ou sem JSON. O arquivo e a URL oficiais continuam sendo a origem
de todos os documentos, com a mesma chave de versão; nenhum schema muda.

Bronze de arquivos conserva bytes originais em `data/raw/<fonte>/<execucao>/`,
incluindo JSON do STJ e HTML do CJF. Não converter ementa ou dispositivo do
espelho em "sentença completa". Dados pessoais eventualmente existentes nos
textos permanecem locais e fora do Git; a triagem IpeaIA de metadados não os
envia automaticamente. Metadados e links podem ser exibidos no painel.

No PostgreSQL haverá migração aditiva; no SQLite a atualização cria somente as
novas tabelas, sem restaurar, apagar ou alterar extrações anteriores. A exportação
portátil inclui as tabelas novas e cria tabelas vazias caso ausentes na cópia
antiga; a ausência não pode ser tratada como dados coletados.

### Consulta pública PJe/TRF1 — `pje_publico_v1` (08/10/2026)

Descoberta confirmada: formulário público `fPP` em
`https://pje1g-consultapublica.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam`.
A ação AJAX de pesquisa vem de `executarPesquisa=function`, não do ID do botão.
O cliente só submete quando o JavaScript publicado indica explicitamente
`if (false) { hcaptcha.execute(); ... }`; desafio ativado/widget/CAPTCHA interrompe
a consulta. Não resolve, altera ou contorna CAPTCHA nem usa login ou credencial.
Cookies/ViewState são efêmeros da sessão pública e não são exportados como credenciais.

Segue apenas links `openPopUp` publicados no resultado do CNJ solicitado,
no host HTTPS oficial: detalhe `DetalheProcessoConsultaPublica/listView.seam?ca=...`
e documentos `documentoSemLoginHTML.seam?ca=...&idProcessoDoc=...` da tabela
`processoDocumentoGridTab`. `ca` é o identificador opaco do link público publicado,
não token institucional nem valor adivinhado. Identidade exige CNJ do resultado,
CNJ rotulado no detalhe e CNJ no cabeçalho do documento e ID rotulado no documento
iguais aos solicitados. Citações a outros processos não criam vínculos.
Variação HTML observada em Formosa: admite também CNJ isolado na terceira linha
do cabeçalho, imediatamente após `Juizado Especial ...` e `Subseção Judiciária ...`
e antes de `PROCEDIMENTO DO JUIZADO ESPECIAL CÍVEL (436)` ou
`CUMPRIMENTO DE SENTENÇA CONTRA A FAZENDA PÚBLICA (12078)` ou
`MANDADO DE SEGURANÇA CÍVEL (120)`. A primeira linha pode ser também
`Vara Federal Cível e Criminal da SSJ de Formosa-GO`. Essa assinatura de
layout exige CNJ completo em elemento próprio e antes dos campos das partes;
não aceita CNJ solto em qualquer posição, citação de precedente ou documento
sem número. Número e ID da assinatura continuam conferidos contra o link.
Outra assinatura observada: `Processo Judicial Eletrônico`, seguido imediatamente
de `RECURSO INOMINADO CÍVEL (460) Nº <CNJ>` no cabeçalho. Esse documento de
Turma Recursal preserva o número de origem; o grau DataJud não é alterado.
Variação SJDF: entre `Processo Judicial Eletrônico` e o recurso, aparecem
`Turmas Recursais dos Juizados Especiais Federais da SJDF` e `3ª Relatoria da
1ª Turma Recursal da SJDF`; abreviação publicada `n.` é equivalente a `Nº`
nesse campo rotulado. O número continua anterior aos dados das partes.
Admite ainda `Seção Judiciária ...`, `<n>ª Vara Federal de Juizado Especial
Cível da SJ<UF>`, CNJ isolado e `AUTOR:` nas primeiras quatro linhas.
Foi observado número de origem do Tocantins entre candidatos cujo órgão atual
DataJud está no recorte: isso NÃO comprova DF/RIDE nem residência. O documento
permanece vinculado ao seu próprio CNJ, sem alterar a população ou geografia.
Layout Luziânia observado: primeiras linhas `PODER JUDICIÁRIO`, `JUSTIÇA
FEDERAL`, `Seção Judiciária do Estado de Goiás`, `JUIZADO ESPECIAL FEDERAL -
SUBSEÇÃO JUDICIÁRIA DE LUZIÂNIA`, `SENTENÇA TIPO "C"`, seguidas de CNJ isolado.
Somente essa assinatura de cabeçalho autoriza número sem rótulo nesse formato.
Formosa também publica `PODER JUDICIÁRIO`, `JUSTIÇA FEDERAL`, `Subseção
Judiciária de Formosa-GO`, `Juizado Especial Cível e Criminal Adjunto à Vara
Federal da SSJ de Formosa-GO`, seguidos de CNJ isolado; aceita-se essa assinatura.
Assinaturas estruturadas têm precedência sobre texto de rótulo. Rótulo
`PROCESSO` deve iniciar linha no cabeçalho anterior aos campos de partes/relator;
`processo nº` em narrativa ou precedente não é identidade do documento.
Documento composto antigo também apresentou, depois do voto, bloco institucional
`JUSTIÇA FEDERAL` / `SEÇÃO JUDICIÁRIA DO ESTADO DE GOIÁS` / `PRIMEIRA TURMA
RECURSAL DOS JUIZADOS ESPECIAIS FEDERAIS` / `GABINETE DA 3ª RELATORIA` /
`RECURSO JEF Nº <CNJ>`. Admite-se somente bloco único com essa assinatura,
CNJ completo no elemento `strong` próprio, fora de `blockquote`, e ID da
assinatura igual ao link. Não selecionar número avulso pelo deslocamento no
corpo; uma citação sem esse bloco institucional não comprova identidade.

Importa somente descritores publicados Sentença/Decisão/Despacho/Acórdão;
outros tipos (petições, comprovantes, certidões) não são o alvo desta coleta.
Não baixa PDF, não pagina documentos nesta versão, não declara autos completos.
Limite/primeira página e quantidade de links são registrados. Vazio da pesquisa
exige indicação explícita do portal; detalhe encontrado sem documento alvo tem
status `sem_documentos`, diferente de ausência de processo ou erro.

Usa `documentos_publicos` existente: `fonte=pje_trf1`, `documento_id=idProcessoDoc`,
`numeros_cnj=[CNJ confirmado]`, `tipo_documento` conforme rótulo publicado,
`texto` do elemento `.folha` sem scripts/estilos. Ementa/decisão/data_decisão e
data_publicação permanecem nulas; data da linha é juntada, não presumida decisão.
Payload normalizado: ID, CNJ, tipo, texto, `extracao_texto=pje_html_publico`,
`versao_parser=pje_publico_v1`, `revisao_privacidade=pendente`.
URL de origem é a consulta pública; recurso_url é o link efetivamente publicado.
Bronze original antes do parser, chave de versão e `store_document` existentes;
somente CNJ explícito permite vínculo a processo já existente, sem nova população.

`coletas.fonte=pje_trf1_publico`, partição `<CNJ>/v1`, parâmetros com limites,
CNJ e parser. Sucesso/vazio/sem_documentos são pulados na retomada; erro ou
bloqueio encerra o lote. Sem documentos novos no piloto, não ampliar automaticamente.
Texto/ementa/decisão/link retidos na API enquanto privacidade pendente, e nenhum
envio automático à IpeaIA. Sem migração ou alteração das tabelas.

### `indicadores_inss_indeferimentos`

Agregados administrativos, não processos nem pessoas identificadas. Campos:
`id` bigint PK; `fonte` varchar(30) = `inss_indeferimentos`; `competencia` integer
AAAAMM extraído do recurso mensal solicitado; `uf` varchar(2); `especie` integer
(87 deficiência, 88 idoso); `motivo` text exatamente como publicado (espaço vazio
vira `Não informado`); `quantidade` bigint; `recurso_id` varchar(500);
`recurso_url`, `arquivo_bruto` text; `hash_arquivo` varchar(64) SHA-256 dos bytes;
`coleta_id` UUID FK coletas; `coletado_em` timestamp UTC. Chave única:
`fonte + competencia + uf + especie + motivo + hash_arquivo`. Uma nova versão
do arquivo gera outro conjunto; NÃO somar snapshots distintos da mesma
competência. O cliente grava manifesto com contagens totais/selecionadas e
filtros. Não armazena data de nascimento, sexo, DER ou outra linha individual
na Silver; os bytes da planilha ficam apenas na Bronze local ignorada pelo Git.

O importador exige cabeçalhos espécie, motivo e UF reconhecidos, filtra espécies
87/88 e UF explicitamente selecionada e só persiste após ler e agregar o
arquivo completo. Espécie é inferida apenas do código numérico da coluna, não
da descrição ou suposição. Colunas inválidas/recurso sem competência comprovada
interrompem a importação. Os motivos não são unidos a processos individuais.

O layout real de agosto/2026 contém título na primeira linha, cabeçalho na
segunda e duas colunas consecutivas `Espécie` (código e descrição). O parser
busca cabeçalho nas primeiras 20 linhas, usa a primeira coluna numérica do par
e valida os códigos linha a linha; não deduz código pela descrição. A competência
de cada linha deve corresponder ao recurso solicitado, inclusive em importação
de arquivo local. Divergência rejeita o arquivo completo antes da Silver.

CAPTCHA/anti-robô será registrado como bloqueio, não contornado e não confundido
com ausência de dados.

### `indicadores_inss_concessoes` — v0.7

Concessões administrativas agregadas, não pessoas únicas, processos ou taxa
de procedência. Fonte mensal CKAN `beneficios-concedidos-plano-de-dados-abertos-jun-2023-a-jun-2025`.
Campos: `id` bigint PK; `fonte` varchar(30) = `inss_concessoes`;
`competencia` integer AAAAMM; `uf` varchar(2); `especie` integer (87/88);
`codigo_despacho` integer; `despacho` text com descrição original ou `Não informado`;
`quantidade` bigint; `recurso_id` varchar(500); `recurso_url`, `arquivo_bruto` text;
`hash_arquivo` varchar(64); `coleta_id` UUID FK coletas;
`coletado_em` timestamp UTC. Chave única: fonte + competência + UF + espécie +
código despacho + descrição despacho + hash arquivo. Snapshots não se somam.
Mudanças nos mesmos bytes com contagem divergente rejeitam a importação.

Layout real agosto/2026: título na primeira linha, cabeçalho na segunda,
colunas consecutivas `Espécie` (código/descrição) e `Despacho` (código/descrição),
`Competência concessão` e `UF`. O importador exige essas colunas, códigos
numéricos, competência compatível em todas as linhas e agrega apenas BPC 87/88
da UF pedida. Só grava após leitura completa. Não persiste CID, nascimento,
sexo, município, escolaridade ou linhas individuais na Silver. O XLSX original
fica exclusivamente na Bronze local ignorada pelo Git.
Não classificar despacho como concessão judicial sem dicionário e validação,
nem atribuir despacho a processo. A tabela é aditiva, compatível SQLite/PG;
cópias antigas sem a tabela ganham tabela vazia, sem dados inventados.

### `indicadores_suas_municipio` — Censo SUAS v0.10

Indicadores contextuais anuais de oferta de serviços socioassistenciais, não
processos, pessoas, beneficiários de BPC nem medidas de cobertura individual.
Na primeira importação, somente os arquivos públicos Censo SUAS 2025 de CRAS
e Postos de Cadastramento do Cadastro Único são usados. Uma linha é a contagem
de identificadores de unidades distintos (`NU_IDENTIFICADOR`) por município,
não contagem de trabalhadores, atendimentos ou usuários. Não criar linhas zero
para município ausente no arquivo.

Campos: `id` bigint PK; `fonte` varchar(30) = `mds_censo_suas`;
`ano` integer; `tipo_unidade` varchar(40) (`cras` ou `posto_cadastramento`);
`codigo_ibge` varchar(7), `municipio_nome` text e `uf` varchar(2) conforme
CSV oficial; `quantidade_unidades` bigint; `url_origem` text;
`arquivo_bruto` text; `hash_arquivo` varchar(64) SHA-256 do ZIP original;
`coleta_id` UUID FK `coletas`; `coletado_em` timestamp UTC. Chave única:
`ano + tipo_unidade + codigo_ibge + hash_arquivo`; um ZIP revisado gera nova
versão, sem somar snapshots. Só é consumido o CSV `Dados Gerais`; arquivos de
recursos humanos e sintaxes SPSS presentes nos ZIPs não são importados para a
Silver. Fonte oficial: [Censo SUAS — Bases e Resultados]
(https://aplicacoes.mds.gov.br/sagi/snas/vigilancia/index2). Os arquivos são
contexto territorial e não autorizam inferir perfil de parte, residência ou
fundamento de decisão a partir do município do órgão julgador. Tabela aditiva,
compatível com PostgreSQL e SQLite; cópias antigas podem criar a tabela vazia.

### Documentos HTML publicados TNU/TRF3/TRF5/TRF6 — v0.9

`documentos-publicados --urls <links oficiais>` aceita até 50 URLs explícitas
das rotas de documento verificadas. Não inventa IDs, não enumera números de
documento, não consulta autos autenticados nem contorna anti-robô. Rejeita URL
com credencial, parâmetro extra/repetido, fragmento ou origem não permitida;
redirecionamento deve manter HTTPS e o mesmo host. Limita cada HTML a 16 MiB.
Cada URL tem sua coleta, Bronze original antes do parser e transação Silver;
falha interrompe o lote sem apagar sucessos anteriores. Vazio temático só é
aceito após reconhecimento do layout; HTML de erro é falha, não ausência.

Usa as mesmas tabelas `documentos_publicos`/`documento_processos`, sem migração.
Na TNU, cada `article` tem ID explícito em `header[id=<id>_1]`; esse ID, não
o ID de pesquisa da URL, é `documento_id`. O CNJ vem exclusivamente de
`.identificacao_processo` do artigo. Cabeçalho real de Reclamação pode incluir
também `PROCESSO ORIGINÁRIO: Nº ...`: nesse layout, o CNJ principal é extraído
somente do segmento anterior ao rótulo explícito, em cada elemento de
identificação. Deve haver um único CNJ principal coerente entre os elementos;
números sem essa separação rotulada continuam rejeitados. O originário permanece
no texto/Bronze, não cria vínculo e não substitui o processo principal.
Extensão compatível de `publicados_html_v1`, sem reescrever documentos anteriores.
No TRF3, o ID vem da URL oficial e o CNJ
do cabeçalho anterior a RELATÓRIO. No TRF5, o ID vem de `tmp.id_documento`, o
CNJ do campo `Processo` em `td.grid` e a data do campo `Data de Julgamento`.
Números citados nos votos/precedentes não criam vínculos. O parser só guarda
documentos com termos temáticos explícitos BPC/LOAS/benefício assistencial;
isso indica corpus candidato, não prova recorte ou concessão inicial.

Na pesquisa pública TRF5 foram observados números anteriores ao padrão CNJ,
como `2009.85.02.502275-8`. O formato estrito `AAAA.NN.NN.NNNNNN-D` é preservado
em `numero_origem`, com `numeros_cnj=[]`, `payload.numero_processo=null`,
`payload.numero_origem` igual ao publicado e
`payload.formato_numero_origem=legado_sem_cnj`. Não completar dígitos, converter
esse número em CNJ ou vinculá-lo a um processo. Formatos não reconhecidos
continuam rejeitados. Extensão compatível do parser `publicados_html_v1`, sem
mudar payloads de documentos CNJ já aceitos nem tabelas.

`trf5-pesquisa` usa o formulário público observado em `pesquisa.wsp`, mantém
cookies de sessão e submete a busca para `/jurisprudencia/resultado_pesquisa.wsp`.
Preserva respostas antes do parsing e pagina pelo campo `grid.pesquisa.next`,
usando o deslocamento publicado no link "Próximo". IDs vêm somente dos links
`javascript:exibir(<id>)` publicados. Valida totais, tamanho da página, número de
linhas, deslocamento seguinte e duplicatas. `--limit` conta URLs de documento;
`--paginas` limita a busca. Reexecuções pulam URLs concluídas na versão corrente
do parser; `--retentar` força nova consulta. Busca LOAS informou 2.233 resultados;
10 documentos foram importados em duas páginas. "Benefício assistencial" também
retornou documentos. Esse total do portal não mede relevância BPC, DF/RIDE ou
cobertura completa. O formulário usa ISO-8859-1 como a página observada.

`texto` conserva o texto publicado normalizado por HTML, sem scripts/estilos;
rodapés de assinatura da TNU e o horário de impressão fora do conteúdo TRF5
não integram o texto analítico, mas permanecem nos bytes Bronze. Não garante
autos completos, anonimização ou classificação do mérito. O campo `decisao`
fica nulo; `ementa` só é preenchida pela seção explicitamente rotulada TRF5.
`payload` registra ID, CNJ, texto, tipo publicado, ementa, data explícita,
`extracao_texto=html_publicado`, `versao_parser=publicados_html_v1`.
Hash de versão usa esse payload, não o horário variável da página inteira.
Nenhum processo novo é criado; só CNJ do cabeçalho idêntico ao já existente
permite vínculo. Corpus permanece local, fora do Git e sem envio automático
à IpeaIA. A triagem atual continua DataJud + TPU com resumo natural.

`tnu-pesquisa` acrescenta descoberta de links pelo formulário público TNU,
sem nova tabela ou envio à IA. Usa `POST /eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados`,
`txtPesquisa`, `selOrigem[]` com valor da opção rotulada TNU no HTML,
`rdoCampo=I` (inteiro teor) e `chkAgruparResultados=on`, com cookies públicos.
Pagina por `ajax_paginar_resultado`, serializando controles do formulário
e alterando `hdnPaginaAtual`; mantém 10 resultados por página. Requer metadados
numéricos, página esperada, contagem de cards e IDs coerentes com os links
`a.inteiroTeor[data-link]`. Mudança de layout/total rejeita a página, não gera
falso vazio. No vazio real da primeira página, o portal omite `value` nos
totais; só aceitar esse caso com título explícito `0 documentos encontrados`
na área de resultados, metadados únicos, página 1 confirmada e nenhum card.
Ausência genérica de valores não é vazio. Bronze guarda página inicial, pesquisa e respostas AJAX antes
da interpretação. Resultados informados não são documentos já coletados.

Só segue links efetivamente publicados. Remove exclusivamente o parâmetro
cosmético de realce `termosPesquisados` (base64 validado), mantendo o ID real
e a rota HTTPS oficial, para não versionar realces como conteúdo novo.
Cada URL baixada usa o contrato `publicados_html_v1` acima. Coletas concluídas
ou vazias tematicamente da mesma URL/versão são puladas; `--retentar` reconsulta
também essas URLs. Repetir avança entre links pendentes dentro das páginas
solicitadas, não além delas; ampliar `--paginas` examina resultados adicionais.
Erros não se tornam vazios. `--limit` conta URLs consultadas, não processos,
pois uma URL agrupada pode conter vários artigos do mesmo processo.

A coleta de busca usa `coletas.fonte=tnu_pesquisa`, partição igual à consulta,
e manifesto em `parametros`: consulta, limites, `versao_busca=tnu_form_v1`,
origem, campo pesquisado, agrupamento, ordenação, tamanho da página, totais
informados, páginas lidas, URLs consultadas/puladas, documentos observados,
versões novas e limite atingido. Cada URL tem sua coleta `tnu` e transação;
sucessos persistem se um documento posterior falhar. A ordem pública pode
mudar entre execuções; não declarar completude nem amostra representativa.

### Jurisprudência publicada TRF6 — v0.9

O formulário público eproc-jur do [TRF6](https://eproc-jur.trf6.jus.br/eproc/) permite pesquisa em inteiro teor, sem autenticação. `trf6-pesquisa` lê as origens rotuladas no próprio HTML (`TRF6`, `TRU6`, `Turmas Recursais`, `Varas Federais`), pagina pelos controles `hdnPaginaAtual`/`hdnTotal*` e segue somente `a.inteiroTeor[data-link]` publicados. O download público `download_inteiro_teor&id_jurisprudencia=...` retorna HTML ISO-8859-1 com o texto da decisão. Não há API REST documentada; trata-se de automação conservadora do formulário público, sujeita a mudança de layout.

Os resultados trazem também link público de consulta processual com CNJ. O coletor valida rotas HTTPS e o parâmetro CNJ tanto no link eproc2g quanto no link PJe1g publicado para Turmas Recursais; não segue esses links nem consulta sistemas fora da pesquisa. Esse CNJ é passado ao parser como identidade esperada e validado no cabeçalho do documento, para que citações a outros processos no voto não virem vínculos. Quando esse metadado não existe ou não confere, a coleta falha em vez de escolher um número arbitrário. Campos persistidos seguem `documentos_publicos` v0.8: `fonte=trf6_jurisprudencia`, `tribunal=TRF6`, texto publicado e Bronze, sem processo novo nem vínculo salvo sem CNJ explícito. Corpus fora da triagem IpeaIA, sujeito a revisão de privacidade antes de qualquer uso analítico/divulgação. O painel/API administrativo devolve somente metadados dessa fonte; texto, ementa, decisão e URL ficam retidos enquanto `revisao_privacidade=pendente`.

Busca BPC observada: TRF6 4.134 resultados, TRU6 19, Turmas Recursais 6.566; Varas Federais retornaram zero em buscas BPC e LOAS. Esses totais informados não são documentos baixados nem casos únicos. Piloto real: 5 URLs por cada uma das origens TRF6/TRU6/Turmas Recursais (15 novos documentos BPC no lote ampliado; corpus TRF6 total: 20 documentos). Tentativas anteriores falharam em dois documentos por múltiplos CNJs citados; a versão corrigida usa CNJ explícito no resultado e confere-o no texto. O vazio só é aceito com título explícito `0 documentos encontrados`, campos de total/página sem valor, página atual 1 e nenhum card; esse controle foi confirmado em chamada real. Nenhum documento foi enviado à IpeaIA.

## Revisão humana no painel — 03/11/2026

Nova tabela aditiva `revisoes_caso`, separada de `extracoes_ia`. Cada gravação é
um evento imutável; a revisão atual é a de maior ID para o processo. Campos:
`id` bigint PK (INTEGER no SQLite); `processo_id` FK processos, indexado;
`autor` varchar(120), nome declarado pelo pesquisador, sem autenticação de identidade;
`estado` varchar(30), `em_revisao` ou `revisado`; `inclusao` varchar(30),
`pendente`, `incluir` ou `excluir`; `resumo`, `motivo`, `observacoes` text;
`evidencias` JSON/JSONB lista de `{documento_id, hash_conteudo, trecho}`;
`criado_em` timestamp UTC. Evidência usa PK local do documento público,
hash da versão e trecho literal do campo texto, com vínculo CNJ explícito
ao mesmo processo. Limites de entrada: resumo/observações 6.000 caracteres,
motivo 3.000, até 50 evidências de até 5.000 caracteres. Conclusão exige
síntese e justificativa; ausência de evidências não é substituída por texto
inventado. Revisão humana não altera resultado bruto ou status da extração IA.

`POST /admin/api/pesquisa/{CNJ}/revisoes` exige `anterior_id` igual à revisão
atual (ou nulo para a primeira), devolve 409 se houver conflito. Escrita
serializada por processo em PostgreSQL e por transação imediata no SQLite.
`GET /admin/api/pesquisa/{CNJ}/leitura` reúne dados do processo, documentos
vinculados, extrações e histórico. Ambos exigem cliente e host loopback,
origem local quando presente e `Cache-Control: no-store`; escrita exige
`X-BPC-Review: 1`. A leitura local é autorizada para análise nesta aplicação;
não promove aprovação de privacidade nem executa chamadas externas à IA.
Esta seção substitui a ausência de ação de revisão descrita na entrega anterior.

`GET /admin/api/pesquisa/fila` permite filtros de CNJ, sede DataJud, assunto,
ano, documentos, estado da revisão e recorte. Recorte padrão: TRF1/G1/JE,
sedes 743/1798/2788 e assuntos 6114/11946/11947 no mesmo registro elegível.
Não equivale ao manifesto congelado de 200 casos. Desmarcar o recorte permite
explorar o cadastro inteiro; documentos são contados por versões vinculadas
explicitamente, sem mistura com corpus sem vínculo. Estado pendente na fila
significa ausência de revisão humana salva. Esses filtros não classificam
concessão inicial nem comprovam residência.

Página inicial `/` e `/admin/analise`: área de leitura e revisão; operações
anteriores em `/admin/coleta`. A tabela é criada aditivamente na inicialização
da API; migração Alembic `20261103_0009` disponível para PostgreSQL. Exportação
portátil conserva revisões e cria tabela vazia em cópias antigas. Ferramentas
de união de bancos precisam remapear também os IDs documentais nas evidências
humanas antes de transportar revisões entre bancos; não usar coincidência de PK.

## IA

### Auditoria local de disponibilidade textual — v1 (08/10/2026)

Artefato JSON local em `data/`, não tabela Silver nem extração IA. Examina todas
as versões de `documentos_publicos` e todas as comunicações. Cada item registra
tipo/ID local, fonte, hash de conteúdo original, campos textuais disponíveis,
SHA-256 de cada campo textual, quantidade de caracteres, vínculos explícitos e
ocorrências lexicais (rótulo, campo, início/fim do intervalo e texto da expressão
de busca encontrada). Não exporta trechos de contexto nem dados pessoais.
Grupos de textos exatamente iguais são identificados por hash, sem apagar versões.
Marca disponibilidade: texto publicado, espelho/ementa ou ausência textual;
isso não certifica inteiro teor, relevância, motivo, procedência ou privacidade.

As pistas de renda, deficiência, idade, demora, cadastro, cessação, concessão
e linguagem dispositiva servem somente para ordenar revisão humana. Citação de
precedente/alegação também pode produzir ocorrência; não converter em resultado
de processo. Estatísticas incluem versões e itens com texto, nunca estimativas
populacionais. O artefato não altera `extracoes_ia` e não é enviado a serviço externo.

### Importação INSS multi-UF — 08/10/2026

`inss-indeferimentos` e `inss-concessoes` aceitam `--ufs DF GO MG` como alternativa
mutuamente exclusiva a `--uf`. A planilha é lida uma vez e cada registro BPC
entra somente no agregado da UF explicitamente selecionada. Deduplicação e
schema permanecem os mesmos; manifesto de coleta registra UFs e contagens por
UF. Validação da competência continua em todas as linhas antes de persistir.
O modo de UF única e seu manifesto continuam compatíveis. Nenhum microdado
individual é persistido na Silver, nenhuma inferência de vínculo judicial.

### Execução portátil sem Docker (05/10/2026)

A base PostgreSQL pode ser exportada para SQLite mantendo as mesmas tabelas,
colunas, chaves, vínculos e dados da aplicação. O módulo `bpc_ingestion.portable`
confere contagens de todas as tabelas, integridade e chaves estrangeiras antes
de publicar `transferencia/bpc-jud.sqlite.gz`. `alembic_version` é metadado
específico do PostgreSQL e não acompanha a cópia; as três views analíticas são
recriadas com sintaxe SQLite. O antigo `SqliteStore` de `processos_raw` é legado
e não deve ser usado para esta cópia.

No SQLite, JSONB usa JSON, UUID usa representação hexadecimal e os IDs usam
INTEGER de 64 bits com geração automática. Campos monetários mantêm o contrato
de duas casas, com a representação NUMERIC do SQLite. Embeddings, se existentes,
são listas JSON; busca vetorial pgvector continua restrita ao PostgreSQL.
Datas seguem o contrato UTC, com leitura sem informação de fuso no SQLite.
O painel e `ipeaia-triagem` usam a cópia definida em `DATABASE_URL` e gravam
`extracoes_ia` nesse mesmo arquivo. A cópia é destinada ao piloto de pesquisa
no ambiente remoto; alterações não sincronizam automaticamente com a origem.
Não executar as migrações Alembic PostgreSQL nesta cópia SQLite.

Todo chunk deve registrar texto, hash, modelo de embedding, dimensão e versão da
pipeline. Toda extração deve registrar modelo, versão do prompt, resultado JSON
e status de validação. A dimensão vetorial será definida quando o modelo for
selecionado; a coluna `vector` aceita armazenamento antes da criação de um índice
específico por dimensão/modelo.

O piloto IpeaIA usa `extracoes_ia.tipo_extracao = triagem_bpc`,
`versao_prompt = bpc_triagem_api_v1.2`, `resultado` JSONB validado e
`status_validacao = pendente`. O modelo vem de `IPEAIA_MODEL` ou `--model`.
Envia apenas campos normalizados de registros públicos TRF1/G1/JE do órgão de
Brasília: classe, órgão, assuntos e movimentos sem complementos, com indicação
de truncamento. Não envia `payload_original`, partes, CPF nem documentos. O
desfecho permanece `indeterminado` sem texto decisório. Cada combinação de
processo, tipo, modelo e versão do prompt é única; uma nova metodologia requer
nova versão, não sobrescrita silenciosa. A classificação não está validada até
revisão humana.

Respostas IpeaIA rejeitadas não são persistidas em `extracoes_ia`. Para diagnóstico,
o CLI salva em `data/ipeaia_rejeitadas/<id>.json` a entrada enviada, modelo,
versão do prompt, erro e resposta da API (token removido). Os arquivos ficam
fora do Git; não são classificações nem registros Bronze imutáveis. O processo
continua pendente. Extrações anteriores v1.0 são preservadas; o prompt v1.1
tem contrato explícito para evidências e não sobrescreve os resultados anteriores.
Por usar outra versão, uma execução v1.1 pode selecionar novamente processos
já triados na v1.0. A versão atual v1.2 também preserva resultados v1.1.

### Resumo natural e contexto TPU — v1.2 (06/10/2026)

`resultado` acrescenta `resumo_caso`: texto obrigatório, não vazio, em português
simples, com até 1500 caracteres. Explica fatos disponíveis, limitações e o que
falta para entender a judicialização, sem inventar negativa administrativa ou
resultado. Os demais campos, incluindo `observacao_curta` (até 300 caracteres),
categorias, evidências e lacunas, são mantidos. O resumo é gerado pela IA e
permanece pendente de revisão humana. É armazenado no mesmo JSON de
`extracoes_ia`, em PostgreSQL ou SQLite; não há tabela nova nem migração.
O painel mostra o resumo e mantém o JSON completo em uma área expansível;
extrações antigas usam `observacao_curta` como alternativa, sem reescrita.

A entrada acrescenta `assuntos[].hierarquia_tpu`, lista de objetos
`{codigo, nome, fonte_arquivo}`, do ancestral ao assunto, consultada em
`referencias_tpu` (`tipo=assunto`). Pais ausentes não são inventados; catálogo
ausente produz lista vazia. Há proteção contra ciclos e limite de 20 níveis.
Na TPU local, 11946 e 11947 descendem de 6114 (Benefício Assistencial), de modo
que seu vínculo temático não deve ser avaliado pelo nome isolado. Isso não
comprova concessão inicial ou motivo da ação. Fonte/contexto ainda é DataJud
mais catálogo TPU; documentos de novas fontes não são enviados neste piloto.
Pendências são selecionadas por modelo e versão; v1.2 pode repetir casos v1.1.

### Decisão sobre conteúdo processual — pesquisa pública de 06/10/2026

Foi confirmada pesquisa pública TRF1/JEF no
[CJF](https://jurisprudencia.cjf.jus.br/trf1/index.xhtml), e o
[TRF1](https://www.trf1.jus.br/trf1/carta-servicos/jurisprudencia) descreve consulta
livre por texto, tipo de documento e fonte TRF1/JEF. O
[arquivo TRF1](https://arquivo.trf1.jus.br/) oferece documentos publicados por
número de processo, não autos completos. Não foi confirmada nesta rodada uma
API pública documentada e viável para baixar em lote petições/sentenças do nosso
recorte. A existência desses portais impede concluir que não há texto público,
mas não demonstra cobertura dos 2.584 processos nem autoriza contornar anti-robô.

O [STJ](https://dadosabertos.web.stj.jus.br/group/jurisprudencia) disponibiliza
espelhos de acórdãos em CSV/JSON/ZIP, com catálogo CKAN testado sem credencial.
É corpus complementar de jurisprudência, selecionado e de outra instância;
não equivale à amostra de concessões iniciais TRF1/DF. Os
[indeferimentos INSS](https://dadosabertos.inss.gov.br/dataset/beneficios-indeferidos-plano-de-dados-abertos-jun-2023-a-jun-2025)
incluem motivos administrativos e ajudam a contextualizar, sem vínculo CNJ
confirmado. Não atribuir esses motivos a um processo individual.

Decisão atual: continuar a triagem de metadados com contexto TPU e resumo
natural para a amostra existente. Foram implementados e testados com respostas
reais os coletores de espelhos STJ, pesquisa CJF/TRF1/JEF1 e agregados INSS.
No piloto inicial foram gravados 5 documentos TRF1, 5 JEF1 e 1 STJ,
sem CNJ coincidente com a amostra nessa etapa. Após as complementações,
a cópia local tem 85 versões documentais: 11 CJF, 21 STJ, 7 arquivo TRF1,
30 TNU e 16 TRF5. Há três vínculos de versões a um único processo BPC do Piauí,
fora DF/RIDE; nenhum novo vínculo documental TNU/TRF5. Esses números são
versões de documentos, não processos adicionais nem cobertura de autos.
A tentativa direta TRF3 ficou `falhou` por timeout, não `sem_resultado`.
O arquivo agosto/2026 INSS
foi lido integralmente: 882.589 linhas, 3.258 indeferimentos espécie 87 e 389
espécie 88 no DF, em 24 agregados. Repetição STJ não duplicou versões.
NLP/Métricas ainda não podem atribuir motivos ou desfechos aos 2.584 processos
originais por essas coletas: os textos estão em corpus separado, com vínculo
restrito ao caso Piauí e sem envio automático à IpeaIA. Índices de ganho e hipóteses de motivação
exigem conteúdo do próprio processo, recorte e validação humana.

O arquivo TRF1 oscilou entre desafio anti-robô e acesso normal. O JavaScript
público `https://arquivo.trf1.jus.br/js/pages/index.js` usa
`POST https://arquivo.trf1.jus.br/localiza_processo.php`, formulário
`ProcInclui=<CNJ sem pontuação>`, sem credencial. A resposta real para
1053078-37.2022.4.01.3400 e casos de 2009/2013 foi
`{"params":"35","existeProcesso":false,"retorno":"..."}`. Não comprovou
disponibilidade de documentos da amostra. O CLI conserva a resposta e distingue
`sem_resultado`, `bloqueada`, `falhou` e `localizado`; a consulta de disponibilidade
agora pode baixar documentos com `--baixar`, após consulta positiva. A busca
de controle pelo CNJ 0058364-48.2010.4.01.0000, citado em publicação oficial
TRF1, retornou documentos DOC. Esse controle é de outro tema: não entra na
amostra BPC. A listagem vem de `POST /PesquisaMenuArquivo.asp`, com `pN`, `pA`
e `p1` provenientes da resposta de localização; o parser exige que a página
informe o CNJ solicitado no cabeçalho `Processo Pesquisado`.
Só baixa links DOC/TIF/TIFF presentes nessa listagem e do mesmo host HTTPS.
Cada arquivo conserva bytes na Bronze; `documento_id` é seu caminho oficial,
`payload` registra CNJ, tipo, publicação, URL, SHA-256 dos bytes e
`extracao_texto=pendente`. `texto`, `ementa` e `decisao` ficam nulos para arquivo
binário: download não equivale a texto convertido. Foi observado também DOC
que é texto simples, com cabeçalho `TRIBUNAL REGIONAL FEDERAL`, sem bytes NUL.
Nesse caso específico `texto` recebe o conteúdo decodificado estritamente em
UTF-8 (ou Windows-1252 se necessário), com `extracao_texto=texto_simples` e
encoding registrado no payload. Não interpretar HTML de erro como documento.
Não executa Word/macros nem
OCR automaticamente. Conversão DOC é separada, descrita abaixo; TIFF/OCR
continua pendente. Os vínculos usam
somente o CNJ explicitamente confirmado pela listagem, sem criar processos.
Limite de arquivos por execução não comprova cobertura de autos completos.
A API de documentos expõe `extracao_texto` do payload para indicar no painel
arquivo binário ainda pendente versus texto simples já disponível. Não é
validação semântica da decisão ou autorização para transmissão de dados pessoais.

### Extração preliminar de DOC legado

`converter-arquivo-trf1` lê somente arquivos já baixados e confinados à Bronze
local. Exige SHA-256 igual ao registrado, limita arquivo a 16 MiB e texto a
2 MiB, não faz chamadas externas e não abre Word/macros. Usa `legacy-doc`
0.2.1, leitor Python de Word 97–2003; não é renderizador completo e não garante
recuperação de formatação, alterações rastreadas, imagens ou conteúdo integral.
Resultado vazio, caracteres de substituição ou falha rejeitam a conversão.
TIFF permanece pendente de OCR.

Uma conversão aceita cria outra versão em `documentos_publicos`, mantendo ID
da fonte, CNJ confirmado, URL, caminho e hash do arquivo original. Não reescreve
a versão pendente. `texto` recebe texto extraído; ementa/decisão não são
classificadas automaticamente. O payload conserva os campos originais e
acrescenta `extracao_texto=doc_legacy_preliminar`, `parser_texto`,
`versao_parser_texto`, `versao_pipeline_texto=trf1_doc_v1`, `sha256_texto` e
`avisos_extracao` (lista). Não copia autor, empresa ou outros metadados pessoais
do documento para o payload. A coleta usa fonte `trf1_arquivo_conversao`.
Deduplicação considera arquivo + versão da pipeline; mesmo arquivo com dois
registros pendentes é convertido uma vez. Sem `--executar` apenas lista
pendências. O texto não entra automaticamente na IA e permanece não validado.

O CJF foi acessado por formulário JSF público, com ViewState e cookies de sessão,
sem credencial institucional, em TRF1/JEF1. Paginação AJAX foi testada em duas
páginas de 30 documentos, sem IDs repetidos. A interface não é contrato REST
estável; mudança de formulário interrompe a coleta em vez de produzir falso vazio.
Não afirmar completude de cobertura. No STJ, os números curtos de recurso e
registro não são CNJ; não criar vínculo automático nem converter número curto.

`cjf-amostra` pesquisa CNJs da base já existente, sem ampliar a população.
Seleção automática: registros públicos (sigilo 0 ou ausente), TRF1/G1/JE,
código municipal DataJud do órgão `743` e assuntos 6114/11946/11947. Isso é
recorte do órgão, não residência nem prova de concessão inicial. A pesquisa
livre aceita CNJ sem pontuação; o portal rejeita hífen no texto livre.
Cada tentativa usa `coletas.fonte=cjf_amostra`, partição
`<CNJ>/<TRF1 ou JEF1>/p<limite de páginas>/v1`, parâmetros com consulta e versão
`cnj_digitos_v1`. Sucessos e vazios da mesma configuração são pulados no
próximo lote; `--retentar` permite nova consulta. Erros/bloqueios continuam
pendentes, interrompem o lote e não são tratados como vazio. O vazio significa
somente ausência de resultado nessa fonte/configuração, não inexistência do
processo. O limite de páginas não comprova cobertura completa.
Documentos são guardados no corpus existente, mas somente CNJ estruturado
coincidente permite vínculo. Uma menção ao número no texto não cria vínculo.
Nenhuma nova tabela ou envio automático à IA é introduzido.

O parser aceita JSON puro ou um único bloco Markdown JSON, sem texto externo.
Caminhos de evidência como `classe.nome`, `assuntos[0].nome` e
`movimentacoes[sequencia=12].nome` são aceitos somente quando existem no registro
efetivamente enviado (não no conjunto de movimentos omitidos por truncamento).
O objeto de evidência mantém exatamente `registro_id` (inteiro da entrada),
`campo`, `referencia` e `sustenta` (textos). `campo` pode ser `classe`, `assuntos`,
`movimentacoes`, `orgao_julgador`, `tribunal` ou `grau`. Os dois últimos são
metadados já enviados e apoiam recorte jurisdicional, não mérito ou residência.
Caminhos são normalizados para o campo raiz, mantendo o caminho original como
prefixo de `referencia`. Referências compostas separadas por `/`, como
`tribunal / grau`, geram uma evidência por componente, somente se TODOS forem
campos/caminhos permitidos e presentes no registro enviado. Preservam o ID,
o texto de sustentação e a referência original com prefixo do campo composto.
Componentes inexistentes ou vazios rejeitam toda a resposta; nenhuma evidência
é descartada silenciosamente. Não há mudança de tabelas ou colunas.
Isso valida estrutura e vínculo, não a interpretação factual, ainda pendente
de revisão humana. Quando a API informa modelo diferente do solicitado, a
resposta é rejeitada com diagnóstico para não registrar atribuição incorreta.

### Analise textual local de comunicacoes publicadas - `comunicacao_bpc_texto_v1`

Correção de 08/10/2026: a minimização protege linguagem dispositiva antes
dos filtros amplos de nomes. O resumo exige texto não vazio até 1500 caracteres;
lacunas exige lista de textos não vazios (lista vazia permitida). IDs booleanos
são rejeitados. Evidências de comunicação também são remapeadas na união,
com validação de processo e hash e auditoria dos IDs de origem/destino.
A minimização continua preliminar, não anonimização garantida; sem envio à IA.

Este tipo e separado de `triagem_bpc` e usa a versao de prompt
`ipeaia_comunicacoes_v1`. Nao altera nem substitui extracoes de metadados. A
entrada e preparada localmente e nao executa chamadas externas nesta versao.
Cada extracao grava em `extracoes_ia` com `tipo_extracao=comunicacao_bpc_texto`,
o identificador real em `modelo` (ou `local-import` para resultado sem modelo),
`versao_prompt=ipeaia_comunicacoes_v1` e
`status_validacao=pendente`; o resumo em portugues e a estrutura ficam em
`resultado`, sem novas colunas ou tabelas.

`resultado` contem `resumo_caso`, `motivo_judicializacao`,
`motivo_administrativo_negativa`, `resultado_judicial`, `evidencias` e
`lacunas`. Cada evidencia contem `comunicacao_id`, `hash_conteudo`,
`trecho_sustentacao` e `sustenta`. A comunicacao deve pertencer ao mesmo
processo; o hash e o trecho precisam corresponder exatamente ao texto publicado.
Sem evidencia suficiente, o campo e `indeterminado`, sem inferencia por tipo
publicado ou metadados.

`motivo_judicializacao` distingue `demora_administrativa`,
`implantacao_beneficio`, `concessao_inicial`, `revisao`, `restabelecimento`,
`outro` e `indeterminado`. Motivo administrativo da negativa e resultado
judicial sao campos independentes; resultado judicial admite
`procedente`, `improcedente`, `parcial`, `extinto_sem_merito`,
`ordem_processual` ou `indeterminado`, sempre com evidencia.

A entrada local exclui CNJ, IDs da parte, partes, CPF, endereco, contato e
identificadores diretos. Remocao deterministica de padroes pessoais e aplicada
antes de persistir a previa; limite de 20 comunicacoes e 60.000 caracteres
redigidos por pacote, excedentes rejeitados sem truncamento. A previa exige
revisao humana de privacidade; nao e autorizacao de envio. Nenhum texto sera
enviado a IpeaIA nesta etapa. Importacao local de resultado exige todas as
evidencias validadas contra o banco e insere uma nova extracao pendente, sem
atualizar ou apagar extracoes anteriores.

### Análise documental PJe — `documento_bpc_texto_v1` (29/10/2026)

Contrato aditivo registrado antes da implementação: `extracoes_ia` conserva
colunas e chave única. Novo `tipo_extracao=documento_bpc_texto`, prompt
`ipeaia_documentos_v1`, schema `documento_bpc_v1`, pipeline `pje_documental_v1`.
Triagem DataJud e análise de comunicações antigas permanecem compatíveis.
Ferramentas antigas de consolidação não devem transportar extrações deste tipo
sem remapear IDs documentais; coincidência numérica não prova identidade.

Entrada: processo existente, documentos `fonte=pje_trf1`, vínculo
`documento_processos.criterio=cnj_explicito`, CNJ da origem igual ao processo,
parser `pje_publico_v1`, texto e hashes conferidos. Jurisprudência complementar
não é documento próprio da amostra. Manifesto congela IDs/hash; mudança exige
nova preparação. Limites: 40 processos por piloto e 30 documentos/120.000
caracteres por processo. Excesso bloqueia o processo explicitamente, sem cortar
texto ou descartar documento silenciosamente. Usar o subconjunto piloto
explícito do manifesto, nunca os primeiros 40 dos 200.

Saída: `resumo_caso` natural (até 3.000 caracteres), `provavel_causa`,
`ato_administrativo`, `negativa_administrativa`, `requisito_controvertido`,
`fundamento_judicial`, `desfecho={resultado,natureza,transito_julgado}`, `lacunas`,
`evidencias`, `versao_prompt`, `revisao_humana=pendente` e
`status_validacao=pendente`. Sem suporte exige `indeterminado`. Resultado:
procedente/improcedente/parcial/extinto_sem_merito/ordem_processual/indeterminado;
natureza: provisoria/final/processual/indeterminado; trânsito: sim/nao/indeterminado.
Final não significa trânsito. Candidato, residência e inclusão definitiva no
recorte continuam sujeitos à revisão humana.

Evidência: `documento_id` (PK local), `hash_conteudo`, `campo=texto`, `inicio`,
`fim`, `trecho`, `sustenta` (campo analítico). Índices Unicode Python, base zero,
fim exclusivo, texto Silver integral: `texto[inicio:fim] == trecho`. Conferir
novamente vínculo e hashes de documento/texto antes da gravação. Citações
`blockquote` da Bronze HTML e regiões textuais identificadas como precedentes
são excluídas como suporte factual. Bronze ausente/divergente bloqueia a
preparação. Caminho histórico ausente pode ser resolvido por `--bronze-map`,
auditoria explícita com um caminho local por documento: reconferir CNJ, ID,
hash do payload, texto e SHA-256 dos bytes HTML descompactados; registrar
caminho original e local sem reescrever `documentos_publicos`. Detecção
automática não certifica interpretação semântica; toda
afirmação substantiva precisa de evidência e revisão humana posterior.

Persistência registra modelo declarado, versões e proveniência de TODOS os
documentos (PK local, fonte, ID de origem, hash de versão, SHA-256 do texto e
da Bronze HTML descompactada),
mais `origem_execucao=importacao_local` ou `ipeaia_api`. Importação local nunca
conta como chamada real. Repetição idêntica é idempotente; divergência na mesma
chave é erro. Nenhum resultado sintético entra na base real.

O plano exige dados pessoais exclusivamente locais. Preparação/dry-run não
autorizam envio; execução documental externa fica bloqueada nesta entrega.
Catálogo autenticado de modelos não recebe texto nem comprova aprovação ética.
Fila reproduzível e importação local ficam disponíveis. Ampliação além de 40
exige gate de qualidade humano; nenhum status é promovido automaticamente.

Painel: `GET /admin/api/processos/{numero}/analise-documental` expõe metadados,
proveniência, estados e lacunas; resumo, narrativas e trechos ficam retidos por
padrão com privacidade pendente. Serialização reutilizável permite leitura local
explícita com `?incluir_texto_local=true`, aceita apenas de cliente loopback e
com `Cache-Control: no-store`, sem autorizar publicação. O endpoint de detalhes existente também
retém o conteúdo deste novo tipo. Não há endpoint que conclua revisão humana.

Preparação reproduzível (usar nomes de saída novos em cada execução):

```powershell
.venv/Scripts/python.exe -m bpc_ingestion ipeaia-documentos-preparar `
  --database data/bpc-consolidado-luna-20261007.sqlite `
  --backup data/ia-documental/ia-backup-20261029-02.sqlite `
  --manifest data/amostragem-inicial/revisao_humana_40.json `
  --output data/ia-documental/fila-piloto-40-20261029-02.json `
  --report data/ia-documental/dry-run-20261029-02.json `
  --bronze-map data/ia-documental/busca-bronze-local-20261029-01.json
```

Mapa opcional: objeto `documentos`, lista de objetos com `documento_id` inteiro
(PK local) e `candidatos_hash_validado` contendo exatamente um caminho local.
O nome desse campo não dispensa reconferência integral pelo backend. Mapa
adulterado, arquivo fora da raiz `--raw-root` ou identidade divergente é rejeitado.
Uma busca local recuperou 64 caminhos históricos por conteúdo, sem nova coleta.
O dry-run final preparou 40 processos/113 documentos, integridade OK, zero FKs,
zero extrações e zero chamadas de geração; revisão humana permanece pendente.

Importação local recebe `--source` com a fila acima e `--results` com lista
`[{"processo_id": <inteiro>, "resultado": <DocumentResult>}]`. Executar primeiro
sem `--executar-local` para validar; só essa opção grava, atomicamente e sempre
pendente. O identificador `--model` é o modelo declarado realmente utilizado;
esse comando não executa nem comprova uma chamada IpeaIA:

```powershell
.venv/Scripts/python.exe -m bpc_ingestion ipeaia-documentos-importar `
  --database data/ia-documental/ia-backup-20261029-02.sqlite `
  --source data/ia-documental/fila-piloto-40-20261029-02.json `
  --results data/ia-documental/resultados-locais-reais.json `
  --model identificador-real-do-modelo-local
```

O arquivo de resultados reais acima ainda não existe: nenhum resultado foi
inventado para preencher a fila. O schema JSON e o prompt completo acompanham
a fila. Detalhes de execução: `data/ia-documental/RELATORIO_PIPELINE_20261029.md`.

## Regras de qualidade

- Datas normalizadas em UTC;
- Payload Bronze nunca corrigido ou sobrescrito;
- Correção de encoding somente nos campos normalizados;
- Checkpoint avança após Bronze e transação PostgreSQL;
- `sem_resultado` no Comunica é diferente de erro;
- Reexecução não cria duplicatas;
- Não inferir concessão ou negativa apenas pela existência do movimento Sentença;
- Não versionar chaves nem o `.env`. Para a transferência solicitada pelo
  pesquisador, `transferencia/bpc-jud.dump` e `transferencia/bpc-jud.sqlite.gz`
  são as cópias autorizadas a
  acompanhar o Git, sem criptografia. Arquivos Bronze continuam fora do Git.

## Log de decisões

| Data | Decisão | Consequência |
| --- | --- | --- |
| 03/11/2026 | Tornar a leitura e revisão por caso o fluxo inicial do painel, com tabela aditiva de revisões humanas e acesso textual local explícito. | Documentos, extrações e linha do tempo podem ser analisados na aplicação. Síntese, motivo, inclusão, citações e histórico humano são persistidos separadamente da IA; identidade/hash/trecho e concorrência são conferidos. Sem chamada externa automática. |
| 12/10/2026 | Coletar a população do Censo 2022 como contexto do denominador etário DF/RIDE, sem derivar elegibilidade individual. | IBGE SIDRA tabela 9514/variável 93: 4.556 linhas de idade para DF + 29 municípios GO + quatro MG da lista oficial Sudeco. CSV, respostas JSON e metadados em `data/raw/ibge_censo2022_ride/`; SHA-256 do JSON `86faa097a773ef8000aff1c165cce1b684a9cf54ce1aeb22a5f59109bc262c4e`. Os 53 valores `-` foram preservados sem conversão para zero. Contexto populacional de 2022, não residência dos litigantes nem medida direta de elegibilidade; fora da Silver e da IpeaIA, sem novo schema. |
| 12/10/2026 | Investigar exportação agregada do IVCAD/Observatório e parar antes de interagir com o painel quando o controle de interface não validou a URL atual do navegador. | Nenhum dado foi exportado e nenhuma interface interna/Qlik foi chamada diretamente; seguir para fontes públicas acessíveis por endpoint/arquivo. CECAD TABCAD permanece separado: exige aceite explícito de Termo de Compromisso de Manutenção de Sigilo, não aceito nesta coleta. |
| 12/10/2026 | Coletar em formato bruto e tabular a população do Censo 2022 para contextualizar o denominador etário do recorte DF/RIDE, sem derivar elegibilidade individual. | IBGE SIDRA tabela 9514/variável 93: 4.556 linhas de idade para DF + 29 municípios de GO + quatro de MG, lista geográfica oficial da Sudeco. CSV, respostas JSON e metadados em `data/raw/ibge_censo2022_ride/`; hash SHA-256 do JSON `86faa097a773ef8000aff1c165cce1b684a9cf54ce1aeb22a5f59109bc262c4e`. Os 53 valores `-` foram mantidos textualmente, sem serem convertidos para zero. É contexto populacional de 2022, não residência dos litigantes nem medida direta de elegibilidade; fora da Silver e da IpeaIA, sem novo schema. |
| 12/10/2026 | Coletar a série regional pública do VIS DATA sobre tempo médio de concessão do BPC e não assumir compromisso de sigilo do TABCAD/CECAD. | Foram preservadas 330 observações (cinco regiões, jan/2021–jun/2026), HTML original e CSV derivado em `data/raw/visdata_bpc_tmc/`; SHA-256 do HTML `ca9e887def9a19b509a9af15c06894942cd9191f23e0cfbbe854d49de56af067`. Para Centro-Oeste em jun/2026, a série informa 187 dias PcD, 109 idoso e 152 total. É contexto administrativo regional, não prazo judicial nem característica de requerentes dos processos; não foi inserida na Silver nem vinculada ao DataJud. O TABCAD público oferece marcação BPC, mas exige aceite explícito de Termo de Compromisso de Manutenção de Sigilo; sem autorização do pesquisador, coleta interrompida antes de submeter consulta ou aceitar termo. |
| 12/10/2026 | Interromper sondagem automatizada da consulta “Pública processual” do Projudi/TJGO quando o formulário apresentou `g-recaptcha-response`. | Nenhum CNJ foi submetido; CAPTCHA não resolvido/contornado; nenhum documento ou processo importado. O corpus TJGO fica pendente de consulta assistida, sem presumir ausência de texto. |
| 12/10/2026 | Incorporar como contexto separado o Censo SUAS 2025 público, limitado a contagens municipais de CRAS e postos de cadastramento; não vincular ao DataJud. | ZIPs oficiais baixados sem autenticação: CRAS 18.561.593 bytes (SHA-256 `e19e0dd825edf739064f838b6405d8689149771dff46bdc971b5c57d5b5b6aa0`) e Postos 5.109.111 bytes (`faad38d3ab8ddfa9d808e281152133f5f6c8cb59a05edeca1f0afdf1609fd314`). Só CSV `Dados Gerais`: 8.903 CRAS em 5.547 municípios e 3.383 postos em 3.010; DF/GO/MG: 1.591 CRAS e 554 postos. Nova tabela `indicadores_suas_municipio`, migração aditiva 0008, contrato v0.10. Duas tentativas iniciais abortaram antes da Silver por erro no mapeamento do campo IBGE7; as falhas ficaram registradas e a importação corrigida foi concluída. SQLite íntegro, zero FK. CSVs de RH e sintaxes SPSS não entram na Silver; ZIPs permanecem locais e fora do Git. Não mede concessões BPC, acesso individual a CRAS ou residência dos litigantes. |
| 12/10/2026 | Continuar a amostragem PJe/TRF1 com duas coortes adicionais de 30 CNJs, excluindo casos já tentados e usando dez seleções SHA-256 por código de órgão DataJud 743/1798/2788; validar individualmente CNJ e ID antes da Silver. | Mais 90 selecionados: 85 consultas concluídas, uma sem documentos-alvo e quatro interrompidas por falha de identidade; 207 novos documentos públicos válidos. Considerando também a retomada histórica, as 140 consultas registram 132 concluídas, uma sem documentos e sete interrompidas; PJe: 523 documentos em 208 processos, corpus 1.058 documentos/531 vínculos. Processos/DataJud/movimentos/Comunica/extrações inalterados: 16.737/16.796/907.521/220/0. SQLite íntegro; zero FK, vínculos PJe sem critério CNJ ou coleta ativa. Documentos individualmente validados antes de falha permanecem; documento com identidade divergente não entra na Silver. Sem processo novo, alteração de schema, envio à IpeaIA, commit/push ou atualização do pacote remoto. O recorte por órgão não comprova residência nem representatividade. Manifests `data/pje-amostra-adicional30-v2-20261012.json` e `data/pje-amostra-adicional30-v3-20261012.json`; detalhes em RELATORIO_PJE_PUBLICO_20261008.md. |
| 12/10/2026 | Ampliar a consulta pública PJe/TRF1 com 30 CNJs inéditos, em quotas iguais por código de órgão DataJud 743/1798/2788 e seleção SHA-256 reproduzível; manter a validação CNJ/ID por documento. | 29 consultas concluídas com 76 documentos novos e um resultado `sem_documentos`; zero falhas de identidade neste lote. PJe: 392 documentos em 151 processos; corpus: 927 documentos e 400 vínculos. Processos/DataJud/movimentos/Comunica/extrações permaneceram 16.737/16.796/907.521/220/0. SQLite `integrity_check=ok`, zero FK, zero vínculos PJe sem critério CNJ e nenhuma coleta ativa. Nenhuma migração, processo novo, envio à IpeaIA, commit/push ou atualização do pacote remoto. Órgão atual não prova residência DF/RIDE; amostra não é estatisticamente representativa. Manifesto `data/pje-amostra-adicional30-20261012.json`; detalhes em RELATORIO_PJE_PUBLICO_20261008.md. |
| 12/10/2026 | Retomar os 38 CNJs restantes do manifesto histórico PJe TRF1 em lotes pequenos, mantendo validação estrita por documento e excluindo da Silver qualquer documento cujo cabeçalho não confirme o CNJ solicitado. | Dos 50 casos selecionados, 47 consultas concluídas e três interrompidas por divergência/ausência de CNJ confirmado no cabeçalho. Foram acrescentados 113 documentos públicos válidos; PJe totaliza 316 documentos vinculados a 122 processos, corpus 851 documentos/324 vínculos. Processos (16.737), registros DataJud (16.796), movimentos (907.521), Comunica (220) e extrações IA (0) inalterados. SQLite íntegro, zero FK e zero vínculos PJe sem critério CNJ. Documentos anteriores individualmente validados são preservados; o documento que falha a identidade não é aceito. Sem novos processos, envio à IpeaIA, alteração de schema, commit/push ou atualização do pacote remoto. Dados não comprovam residência DF/RIDE nem cobertura completa. Detalhes em RELATORIO_PJE_PUBLICO_20261008.md. |
| 08/10/2026 | Ampliar PJe para anos 2020–2022 e encerrar o lote ao constatar divergência real entre CNJ solicitado e cabeçalho publicado. | Mais 45 documentos válidos de 12 processos: PJe totaliza 203 textos em 85 processos; corpus 738 e vínculos 211, sem população nova. Manifesto histórico de 50: 12 consultados, 11 concluídos, um parcial e 38 não consultados após a interrupção. Documento 469433861 solicitado em 1001481-85.2020.4.01.3501 declara 1001906-15.2020.4.01.3501 no cabeçalho; rejeitado e ausente da Silver, sem presumir erro de digitação ou vínculo. Fonte de conteúdo permanece PJe público verificado + atos publicados, não CRPS nem autos completos. Parser reconhece abreviação N., cabeçalho recursal SJDF e bloco institucional único após voto, sem aceitar CNJ avulso/citação. Auditoria integral: 203 documentos, hashes/IDs/vínculos e 538 gzip; SQLite OK, zero FK, 183 testes aprovados. Três CNJs têm origem fora das três sedes principais; localização não prova residência. Último estado das 88 consultas: 83 concluídas, três sem documento alvo, duas parciais; 15 falhas históricas preservadas. Sem envio à IA, alteração de schema, commit/push ou atualização do pacote remoto. Encerramento desta tentativa segue a instrução de parar em falha não solucionável sem presumir identidade; não significa esgotamento dos portais. Detalhes em RELATORIO_PJE_PUBLICO_20261008.md. |
| 08/10/2026 | Incluir consulta pública PJe/TRF1 como fonte viável de conteúdo individual, usando ação AJAX publicada e documentos HTML com CNJ/ID confirmados. | 158 documentos novos (68 sentenças, 41 decisões, 45 despachos, quatro acórdãos) ligados a 73 processos existentes; corpus 535 → 693 e vínculos 8 → 166. Foram consultados 76 CNJs: 72 concluídos, três sem documentos alvo na primeira página e um parcial com documento sem CNJ rejeitado. Dois CNJs têm origem Goiânia/Tocantins apesar de órgão atual no recorte; não provar DF/RIDE/residência. Originais locais: 439 gzip verificados, todos os 158 documentos reprocessados com hash/identidade/vínculo conferidos; SQLite íntegro e 181 testes aprovados. Nenhum login/CAPTCHA contornado, nenhuma migração/população nova/envio à IpeaIA. Fonte de conteúdo processual passa a incluir o texto judicial público verificado do PJe, além de atos do Comunica; não são autos completos. Triagem de metadados não passa a consumir textos automaticamente. Coleta ampliada em lotes 20/50, retomadas deduplicadas e falhas históricas preservadas. Demais fontes: Comunica em manutenção, CJF/JEF1 sem resultado nos dez novos CNJs, diários históricos inacessíveis; CRPS administrativo separado. Detalhes em RELATORIO_PJE_PUBLICO_20261008.md. |
| 08/10/2026 | Ampliar cinco portais de jurisprudência, completar INSS janeiro–agosto/2026 DF/GO/MG e inventariar textos localmente sem classificação automática. | 303 versões novas: 535 documentos, oito vínculos explícitos e 16.737 processos preservados. INSS: 211 grupos novos de indeferimentos e 98 de concessões, com leitura multi-UF única e validação integral. Auditoria de 755 itens com hashes/posições e cinco leituras qualitativas dirigidas; pistas não equivalem a motivo/desfecho. TNU distingue cabeçalho principal de PROCESSO ORIGINÁRIO, sem vinculá-lo; coleta interrompida preservada e retomada concluída. Comunica mantém 503; CRPS pendente. Sem envio à IA ou mudança de tabelas. Fonte de conteúdo individual não muda: texto vinculado quando disponível, indeterminação quando ausente; detalhes em REVISAO_E_AMPLIACAO_FONTES_20261008.md. |
| 08/10/2026 | Ampliar autonomamente jurisprudência pública TNU/TRF2/TRF4/TRF5/TRF6 e indeferimentos INSS de maio/2026 para DF/GO/MG; manter CRPS pendente de acesso assistido. | 59 versões novas: corpus 173 → 232, dois vínculos CNJ explícitos TRF6 a processos existentes, sem processo novo. INSS: 26.401 indeferimentos em 63 agregados novos, sem atribuição individual de motivo. Sondagem Comunica retornou 503; lote não retomado. Sem alteração de schema ou envio à IA; pacote de transferência não atualizado. Detalhes em RELATORIO_COLETA_AUTONOMA_20261008.md. |
| 08/10/2026 | Publicar respostas Comunica como membros gzip completos por troca atômica e interromper indisponibilidade sustentada. | Impede perder a validade do gzip já publicado por ausência de trailer no encerramento abrupto; preserva respostas anteriores e arquivos legados. Ctrl+C marca falha, três erros temporários consecutivos/bloqueio param o lote. Sem nova coleta real, alteração de schema ou envio à IA. |
| 08/10/2026 | Selecionar até 400 CNJs inéditos para Comunica com quotas 200/100/100, investigar os diários históricos TRF1 e testar cinco consultas públicas PJe. | Manifesto Comunica `20261010` salvo antes da coleta; 3.135 elegíveis após exclusões e 400 selecionados, mas a API sustentou HTTP 503: interrompido após 10 consultas/50 tentativas limitadas, zero novas comunicações, 390 pendentes; Bronze parcial e coleta `falhou` preservados. O acervo judicial histórico não foi acessível pelos links oficiais testados; nenhum diário foi importado ou vinculado. PJe respondeu HTTP 200 sem confirmar resultado/documento; sem login/CAPTCHA resolvido. CRPS exige conta gov.br e fica para consulta direta pelo pesquisador. Banco permaneceu íntegro, sem mudança de schema, sem texto enviado à IpeaIA. |
| 08/10/2026 | Ampliar corpus TRF6 por LOAS e verificar rotas TRF3/consulta processual TRF1; exportar pacote corrigido sem sobrescrever anterior. | Cinco documentos novos TRF6: 173 versões, 16.737 processos, 220 comunicações e quatro vínculos. TRF3 e consulta legada TRF1 expiraram no acesso direto, sem falso vazio. Novo pacote `transferencia/bpc-consolidado-luna-20261008-corrigido.sqlite.gz` inclui a coleta; originais/extrações preservados, nenhum texto enviado à IA. |
| 08/10/2026 | Corrigir minimização, validação textual e remapeamento das evidências de comunicações; permitir pacote corrigido datado via Git. | Linguagem dispositiva preservada; resumo/lacunas validados; IDs de comunicação conferidos por origem/processo/hash. Exceção Git apenas `transferencia/bpc-consolidado-luna-20261008-corrigido.sqlite.gz`, sem commit/push automático. Snapshot não incorpora coletas posteriores; textos públicos não anonimizados exigem cuidado com divulgação. |
| 08/10/2026 | Definir analise textual separada para comunicacoes publicadas, inicialmente local, antes de introduzir o modo. | Tipo `comunicacao_bpc_texto`, prompt `ipeaia_comunicacoes_v1` e JSON em `extracoes_ia`; evidencias obrigatorias por ID/hash/trecho, campos de judicializacao/negativa/resultado separados, revisao pendente e entrada minimizada. Sem chamadas externas ou alteracao da triagem `triagem_bpc`. |
| 08/10/2026 | Auditar o gzip interrompido, registrar revisao rastreavel de dez textos e gerar pacote SQLite novo para transferencia controlada. | O gzip da coleta `8ed0515fabfb45b89671e6768f730c02` permaneceu intacto; 136 consultas sem Bronze verificavel foram reconsultadas em nova coleta `28a0d9a73da5405f833f2acb1dc49334` (136 HTTP 200, 41 itens observados, zero novas apos deduplicacao; nenhum bloqueio repetido). Manifestos locais ficam em `data/` fora do Git. A revisao de 10 textos (6 sentencas, 4 decisoes) identificou fundamentacao/dispositivo em 10/10 e motivo administrativo explicito em 0/10; o manifesto contem CNJ/ID/hash e conclusoes sem trechos pessoais. Modo textual local usa `comunicacao_bpc_texto`/`ipeaia_comunicacoes_v1`, evidencia vinculada e revisao pendente; nenhuma chamada externa e triagem de metadados intacta. Pacote `transferencia/bpc-consolidado-luna-20261008.sqlite.gz`: 19 tabelas, 16.737 processos, 220 comunicacoes, SHA-256 `b22e9de6974cc0fe78056e1e669be6b1a2ff3f7b39181eae0d57950b494e9113`; copia validada com integridade OK e zero violacoes FK. Exige revisao de privacidade antes de publicacao; sem Bronze/diagnosticos no Git, sem commit/push e sem alterar o submodulo. |
| 08/10/2026 | Testar a base TRF1 do CJF em 10 CNJs adicionais do manifesto do piloto e inspecionar o link do documento JEF1 `000046005`. | Dez consultas concluídas sem resultado, com Bronze e status preservados no SQLite consolidado; zero documentos ou vínculos novos. Subamostra corresponde às primeiras dez linhas do manifesto, não representa os 200 casos. O link “Acesse Aqui” aponta à consulta genérica PJe2g, não ao inteiro teor; tentativa de acesso interrompida por redirecionamento fora do host permitido. Não concluir ausência de decisão nem disponibilidade de autos. Priorizar expansão Comunica por CNJ, que já demonstrou ganho no piloto, mantendo a distinção entre publicação e autos completos. |
| 08/10/2026 | Remapear IDs DataJud embutidos nas evidências de extrações durante a consolidação e validar seu processo. | Evita ligar evidências a outro caso quando os IDs locais colidem. Referências inválidas interrompem a união; relatório conserva IDs de origem/destino. Sem mudança de schema nem reinterpretação dos resultados da IA. |
| 06/10/2026 | Ampliar pesquisa TNU com termo específico "benefício de prestação continuada" e confirmar disponibilidade TRF3. | TNU: 10 URLs novas/16 documentos, total 30 documentos e 16 CNJs distintos. Corpus total: 85 versões, 2.584 processos e três vínculos anteriores; integridade SQLite OK. TRF3 documenta consulta pública de acórdãos por CNJ, mas as páginas oficiais expiraram por timeout na coleta direta; zero documentos importados. |
| 06/10/2026 | Automatizar busca e paginação pública TRF5 com retomada por documento já coletado. | Consulta LOAS (2.233 resultados informados) percorreu duas páginas e importou 10 documentos; busca acentuada "benefício assistencial" também funcionou. Base local: 69 versões (16 TRF5), 2.584 processos e três vínculos anteriores; integridade SQLite OK. Total portal não equivale ao total BPC/DF/RIDE. Textos seguem fora da IpeaIA. |
| 06/10/2026 | Descobrir links TNU pelo formulário público e paginação AJAX, com retomada por URL já coletada na mesma versão. | Busca LOAS informou 534 resultados; duas páginas reais tiveram 20 links distintos. Piloto coletou 3 URLs/6 documentos; repetição pulou essas URLs e coletou outras 2/2 documentos. TNU local: 14 documentos de 6 CNJs; total de corpus 54 versões. Os 2.584 processos e três vínculos anteriores foram preservados. Não significa cobertura DF/RIDE, nem envio de texto à IA. |
| 06/10/2026 | Integrar documentos HTML publicados TNU/TRF3/TRF5 por URLs oficiais explícitas, usando o corpus versionado existente. | Coleta real TNU: seis documentos; TRF5: um documento. Reexecução: zero versões novas. CNJ só do cabeçalho/campo Processo; população original permanece 2.584. Textos locais, não anonimizados nem enviados à IA. Contrato v0.8 sem migração; descoberta automática de links pendente. TRF3 teve timeout e coleta `falhou`, sem dados gravados dessa fonte. |
| 06/10/2026 | Pesquisa adicional confirmou exemplos públicos de texto decisório na TNU, TRF3 e TRF5; priorizar piloto textual complementar, sem ampliar silenciosamente a amostra. | CNJs reais TNU `5006875-14.2022.4.04.7005` e TRF3 `5000929-32.2025.4.03.6343`, com relatório/voto acessíveis. Fontes e links em `FONTES_ABERTAS.md`; ainda não importados. Não comprovam cobertura DF/RIDE nem API de lote. Triagem atual continua DataJud + TPU, resumo natural v1.2 e revisão pendente; não envia esses textos nem determina motivo/desfecho individual. |
| 06/10/2026 | Integrar concessões públicas INSS como contexto agregado por competência/UF/espécie/despacho, em tabela separada. | Leitura integral agosto/2026: 848.996 linhas; DF: 1.495 concessões espécie 87 e 667 espécie 88, em 8 grupos. Não são processos, pessoas únicas nem taxa de procedência. Microdados só na Bronze local; sem vínculo CNJ nem envio à IA. Contrato v0.7/migração aditiva 0007. |
| 06/10/2026 | Extrair preliminarmente texto de DOC legado em Python, sem Office/macros/rede e sem sobrescrever originais. | Dois arquivos reais convertidos: ementa BPC (3.217 caracteres) e decisão de controle (5.614). Leitor/pipeline/hash registrados; revisão humana e integridade textual não comprovadas. TIFF/OCR pendente. Não altera recorte nem envia textos à IA. |
| 06/10/2026 | Implementar download do arquivo TRF1 após localização positiva e confirmação do CNJ na listagem. | Controle positivo oficial e um BPC de 2006 no Piauí foram localizados; certidão/ementa deste último geraram dois vínculos reais com a base. Ele fica fora DF/RIDE. Texto simples lido; DOC binário/OCR TIFF pendentes, sem envio à IA. Originais preservados localmente. |
| 06/10/2026 | Acrescentar busca CJF por CNJ da própria amostra, com lote retomável e vazio separado de erro. | Consulta real: 10 TRF1 e 5 JEF1 sem resultados nos limites pedidos; busca de controle com CNJ já conhecido retornou documento. Repetição JEF1 avançou aos próximos pendentes. Não comprova falta de decisões nos autos. Vínculo exige CNJ estruturado; textos seguem locais e não são enviados à IA. |
| 06/10/2026 | Incluir histórico ZIP oficial STJ mediante `--historico`, com Bronze antes do parsing e limites de expansão. | Coleta real acrescentou 20 documentos históricos da Segunda Turma; corpus local agora tem 31 documentos (21 STJ, 10 CJF), zero vínculos. Os 2.584 processos originais não foram alterados. Histórico completo e textos do recorte continuam não comprovados; sem envio automático à IA. |
| 06/10/2026 | Integrar corpus CJF/TRF1/JEF1 e STJ, e agregados de indeferimentos INSS; testar disponibilidade no arquivo TRF1 sem bypass. | 11 documentos e 24 agregados reais na cópia SQLite local; zero vínculos com a amostra. Novas tabelas aditivas, origem/versões preservadas. Arquivo TRF1 sem documentos localizados nos CNJs testados; download DOC/TIFF segue pendente. Dados novos não acompanham o Git nem entram automaticamente na IpeaIA. |
| 06/10/2026 | Prompt v1.2: resumo natural no JSON de extração e hierarquia TPU na entrada; pesquisar fontes públicas adicionais sem misturar populações. | `resumo_caso` até 1500 caracteres, sem novas tabelas; resultados anteriores preservados. CJF/TRF1 e STJ são fontes candidatas de textos, mas nenhuma coleta de documentos foi integrada. Motivo e desfecho continuam não determináveis só por metadados. |
| 06/10/2026 | Versionar prompt de triagem em v1.1, explicitar formato e permitir evidências de `tribunal`/`grau`; desmembrar campos compostos válidos separados por `/`. | Resolve incompatibilidade `tribunal / grau` sem inventar vínculos nem descartar evidências. Metadados já enviados; enum de `campo` ampliado neste contrato. Resultados v1.0 preservados e passíveis de nova triagem v1.1. |
| 07/10/2026 | Ampliar a coleta DataJud TRF1 para municípios da RIDE-DF observados na base (Formosa e Luziânia), graus G1/JE e assuntos-alvo; preservar separação entre população e documentos públicos. | Lotes concluídos: 1.950 hits DataJud no total; a população local passou de 2.584 para 4.531 processos (+1.947 líquidos) e 4.536 registros. Não é censo da RIDE: códigos observados (1798/2788) não têm formato de código IBGE de 7 dígitos descrito pelo DataJud; associação validada pelo nome do órgão e lista oficial Sudeco. 85 versões documentais e 3 vínculos inalterados. SQLite íntegro, sem violações FK. |
| 07/10/2026 | Mapear jurisdição oficial vigente da RIDE e coletar candidatos de subseções TRF1 associadas e da subseção Unaí/TRF6. | Resolução Presi TRF1 13/2026 e lista TRF6/Unaí confirmam cobertura territorial de cidades da RIDE. Coletados 1.000 hits em cada código TRF1 743/1798/2788/216/5332/1903 e 4.314 hits completos no código TRF6 3170404. Base local: 11.865 processos e 11.922 registros (+7.334 processos líquidos nessa rodada); pool de sedes de Goiânia/Anápolis/Uruaçu e TRF6 permanece separado como suplementar, pois sede/competência não prova residência nem substitui o recorte principal TRF1. Documentos: 85 versões, 3 vínculos. Integridade SQLite OK, sem violações FK. |
| 07/10/2026 | Corrigir normalização de `assuntos` após payload real do TRF1 retornar lista aninhada e código sem nome. | Parser achata recursivamente listas para objetos `{codigo,nome}`; código sem nome fica `nome: null`; Bronze e payload preservam a fonte sem mudança. Sem migração ou alteração do contrato normalizado. 13 testes DataJud e 99 testes da suíte passaram com SQLite em memória. PostgreSQL não foi testado: ambiente Windows bloqueia o binário `libpq`. |
| 05/10/2026 | Aceitar bloco Markdown JSON e normalizar caminhos de evidências existentes; rejeitar divergência de modelo informada pela API. | Corrige incompatibilidade de formato observada no GLM sem aceitar caminhos inexistentes nem mudar o schema; preserva rastreabilidade do caminho em `referencia`. |
| 05/10/2026 | Detalhar falhas de evidências e conservar respostas IpeaIA rejeitadas em diagnóstico local sem token. | Não aceitar IDs externos à entrada nem formatos inválidos; nenhuma extração gravada para o processo rejeitado e nenhuma repetição automática. Sem alteração do schema ou da metodologia. |
| 05/10/2026 | Usar cópia SQLite no servidor remoto sem Docker; manter PostgreSQL na origem. | Mesmas tabelas e dados da aplicação; extrações de IA persistidas em `data/bpc-remote.sqlite`. Embeddings armazenados como JSON, sem busca pgvector nesse ambiente. |
| 07/10/2026 | Integrar busca pública de inteiro teor TRF6 com parser que valida identidade CNJ contra o resultado e o documento. | `trf6-pesquisa` importou 10 decisões da origem TRF6, cinco da TRU6 e cinco das Turmas Recursais (20 documentos no corpus); Varas Federais sem resultados BPC/LOAS. Nenhum processo novo ou vínculo presumido. Parser evita confundir citações no voto com o processo julgado. Texto não enviado à IpeaIA e API do painel retém texto/link até revisão de privacidade. |
| 07/10/2026 | Incluir candidatos DataJud TJMG de quatro municípios mineiros da RIDE e terminar lote Comunica PJe retomável; testar outras fontes já mapeadas. | 361 registros TJMG (274 Arinos, 52 Buritis, 35 Unaí; Cabeceira Grande sem hits), a validar como competência delegada; 100 processos consultados no Comunica e 13 novas comunicações. Arquivo TRF1 acessível, mas um lote de cinco CNJs não encontrou julgados publicados; segunda tentativa TRF3 expirou por timeout. Não contornar CAPTCHA/credenciais nem usar API institucional de notícias como dados de processo. |
| 07/10/2026 | Integrar busca pública de inteiro teor BPC no eproc/TRF4 com validação de CNJ do card e paginação oficial. | Portal respondeu sem credencial; buscas BPC reportaram 6.917 resultados TRF4, 443 TRU4 e 25.342 Turmas Recursais. `trf4-pesquisa` coletou 10 documentos TRF4, cinco TRU4 e cinco Turmas Recursais (20 no total) em três lotes; não criou processos nem vínculos automáticos. Persistidos no PostgreSQL configurado (2.584 processos/2.588 registros); a cópia SQLite `data/bpc-remote.sqlite` não foi sincronizada nesta coleta. Origem suplementar fora do recorte principal TRF1/DF. Texto/link retidos na API até revisão de privacidade e nenhum documento enviado à IpeaIA. Contrato v0.9 sem migração; 111 testes da suíte passaram. |
| 07/10/2026 | Investigar TRF3/TJMG e testar importação STJ já prevista no contrato, sem misturar corpora judiciais. | Pesquisa TRF3 expirou por timeout de 90s; TJMG respondeu HTTP 401 com desafio “Informe o código” (CAPTCHA), sem contorno. Importação STJ salvou 1 documento BPC/LOAS no corpus `stj`; lote interrompido durante o próximo recurso e marcado `falhou` com 1 registro. Sem processos ou vínculos presumidos, sem envio à IpeaIA e sem mudança de schema. |
| 07/10/2026 | Integrar pesquisa pública eproc/TRF2, TRU2 e Turmas Recursais por busca BPC, com validação CNJ e paginação. | Portal oficial respondeu sem credencial; consultas BPC reportaram 5.927 hits TRF2, 29 TRU2 e 16.367 Turmas Recursais. `trf2-pesquisa` coletou 10 decisões TRF2, cinco TRU2 e cinco de Turmas Recursais (20 versões); CNJ do card coincide com parâmetro da rota e cabeçalho do documento. Sem processo/vínculo automático. PostgreSQL: 2.584 processos, 2.588 registros e 40 documentos publicados nas rodadas TRF2/TRF4; SQLite remoto não sincronizado. Texto/link ocultos na API até revisão de privacidade e sem envio à IpeaIA. TRF2 fora do recorte principal TRF1/DF; contrato v0.9 sem migração; 117 testes passaram. |
| 07/10/2026 | Testar e coletar DataJud TJGO para os 29 municípios goianos da RIDE, assuntos 6114/11946/11947, graus G1/JE e payload essencial. | Sudeco lista os municípios e os códigos foram resolvidos pelo serviço oficial do IBGE. DataJud reportou 4.513 hits; coleta retomável terminou com 4.513 registros e 4.513 CNJs distintos. PostgreSQL passou de 2.584 para 7.097 processos (4.513 novos) e de 2.588 para 7.101 registros. Não confirma competência federal delegada nem residência na RIDE; manter grupo TJGO separado. SQLite remoto não foi sincronizado. Nenhuma migração de schema. |
| 07/10/2026 | Consolidar em SQLite novo o PostgreSQL ativo, `data/bpc-remote.sqlite` e o pacote SQLite de transferência, com chaves lógicas e relatório de conflito. | Snapshot PostgreSQL somente leitura; originais preservados. IDs locais remapeados, FKs e unicidade verificadas. Conflitos ficam no JSON com as duas origens; hashes divergentes de documentos são versões, snapshots agregados não se somam. Operação fora do schema Silver, sem migração. |
| 07/10/2026 | Consultar manifesto reproduzível de 50 CNJs TRF1/DF e subseções de Formosa/Luziânia no CJF/JEF1, Arquivo TRF1 e Comunica PJe; expandir a 200 após vínculo correto e execução estável. | Manifesto estratificado por ano e assunto TPU, semente `20261007`. Resultados negativos e positivos são preservados por fonte. Comunicações são atos publicados, não autos. Vínculo documental exige CNJ explícito; sede de órgão não prova residência. Cobertura final fica no relatório de execução. |
| 07/10/2026 | Adicionar `--manifest` explícito a `cjf-amostra` e selecionar INSERT compatível com SQLite/PostgreSQL. | A seleção automática do CJF continua limitada a Brasília; um CSV explícito aceita até 200 CNJs e não altera a população. Testes SQLite cobrem colisões locais, TPU, FKs, comunicações e recusa de saída existente. Sem schema novo. |
| 07/10/2026 | Executar P1 até 200 CNJs, P2 em cinco fontes complementares e P3 para três competências INSS DF/GO/MG. | P1: 200 CNJs consultados; 35 tiveram publicações, 13 tiveram sentença/decisão/acórdão e 0 tiveram motivo administrativo explícito. Arquivo TRF1: 200 sem resultado. P2: 25 URLs e 21 versões suplementares sem vínculos automáticos. P3: 202606–202608 com agregados por UF, reutilizando recursos e deduplicando agosto DF pelo hash. Resultados, numeradores/denominadores e limites em `RELATORIO_EXECUCAO_COLETA_LUNA.md`. Sem alteração de schema. |
| 08/10/2026 | Retomar as 64 consultas pendentes do manifesto Comunica `20261008` e ampliar com mais 200 CNJs inéditos, nas quotas 100/50/50, usando o SQLite consolidado explicitamente. | Os dois lotes foram concluídos sem bloqueio: 400 CNJs consultados, 68 com publicações, 110 itens observados e 110 novos após deduplicação; o banco passou de 110 para 220 comunicações e não criou processos. Entre os 400, 10 CNJs têm rótulos sentença/decisão (7 sentença, 4 decisão com 1 sobreposição; 0 acórdão); revisão de 10 textos não identificou motivo explícito de indeferimento. O Bronze da execução interrompida anterior permanece preservado e ilegível por gzip truncado; ela segue `falhou`. Integridade SQLite `ok`, zero violações FK, processos/documentos/extrações preservados, sem schema novo. Detalhes por grupo/ano, hashes, IDs e limites em `RELATORIO_AMPLIACAO_COMUNICA_20261008.md`. |
| 12/10/2026 | Coletar do SIDRA o Censo 2022 de pessoas com deficiência por grupo etário nos municípios da RIDE-DF, sem criar integração analítica individual. | Tabela 10131, variável 11852: 2.754 linhas para 34 municípios (27 faixas/grupos etários × 3 categorias de deficiência). 131 células vieram como `-` e foram preservadas; 115 somas numéricas diferem em somente uma pessoa por arredondamento. JSON, metadados, CSV e manifesto em `data/raw/ibge_censo2022_ride/`. Contexto agregado; não mede elegibilidade BPC, não identifica litigantes, fora da Silver e da IpeaIA. |
| 12/10/2026 | Coletar estatísticas públicas de rendimento municipal do Censo 2022 para contextualizar desigualdades no recorte DF/RIDE, sem inferir condição econômica individual. | SIDRA tabela 10295, variáveis de rendimento nominal médio e mediano mensal domiciliar per capita: 68 valores (duas variáveis × 34 municípios), todos disponíveis. JSON, metadados, CSV e manifesto em `data/raw/ibge_censo2022_ride/`. A definição exclui algumas condições de moradia; são estatísticas agregadas de 2022, não renda de litigantes nem elegibilidade BPC. Fora da Silver e da IpeaIA. |
| 12/10/2026 | Coletar a série administrativa pública de BPC do VIS DATA 3 por município pagador para os 34 municípios do recorte RIDE-DF, sem misturá-la a processos judiciais. | Sem login. Série anual 2004–2024: 714 linhas (21 × 34). Série mensal: 8.243 linhas, 244 referências esperadas de 01/2004 a 04/2024; 32 municípios têm todas, Cabeceira Grande tem 40 referências ausentes e Vila Propício 13. Gaps mantidos como ausência, sem imputar zero. JSONs, CSVs e manifestos/hashes em `data/raw/mds_visdata_bpc_municipio_ride/`. Município pagador não prova residência; agregado não é processo nem pessoa individual. Fora da Silver e da IpeaIA. |
| 12/10/2026 | Retomar exportação dos agregados públicos do IVCAD/Observatório sem credenciais nem chamada direta às interfaces internas do Qlik. | A interface CUA retornou inventário vazio (`apps=[]`, `browsers=[]`) e não disponibilizou o navegador embutido (`Browser is not available: iab`). Nenhum dado foi exportado e nenhum endpoint interno do Qlik foi chamado. Como rota alternativa sem interface, a coleta prosseguiu no endpoint público do VIS DATA 3, registrada acima; IVCAD permanece pendente até haver navegador acessível. |
| 13/10/2026 | Retomar e concluir a amostra pública do Comunica/DJEN de 400 processos TRF1 (Brasília, Formosa e Luziânia), sem autenticação e sem confundir publicações com inteiro teor. | 400/400 consultas concluídas: 41 processos com publicações e 359 sem resultado (31/200 Brasília, 4/100 Formosa, 6/100 Luziânia); 82 comunicações novas, total 302. O banco permaneceu com 16.737 processos, 16.796 registros DataJud, 907.521 movimentos, 1.058 documentos, 531 vínculos e zero extrações IA; consultas PJe 851→1.241. Bronze gzip íntegra (389 linhas na execução principal), SQLite `integrity_check=ok`, zero violações FK e zero duplicatas processo/hash. Backup pré-coleta `data/backup-pre-comunica-djen-20261012.sqlite` (SHA-256 `3a8a25d99350defd1b0f766939f0758ae5c520505c9e69234cabc28f51d5aea`). Sem alteração de schema, envio à IpeaIA, commit ou push. “Sem resultado” não prova inexistência de ato ou de autos; Comunica contém publicações, não peças/inteiro teor. Detalhes em `RELATORIO_COLETA_COMUNICA_DIARIOS_LUNA.md`. |
| 13/10/2026 | Ampliar sem credenciais o corpus público de decisões BPC no CJF/JEF1 por pesquisa temática `BPC`, com paginação retomável e vínculos apenas por CNJ explícito. | O portal reportou 1.092 resultados em 37 páginas; todas consultadas e preservadas: 1.092 acórdãos com texto/CNJ, sem chaves duplicadas; 42 arquivos brutos HTML/XML gzip íntegros. Sete documentos vinculados por CNJ explícito a seis processos existentes, sem criar processos. Corpus `documentos_publicos` 1.058→2.150; processos 16.737, vínculos 531→538; zero extrações IA. Coletor ganhou `--pagina-inicial` para retomar páginas CJF sem alterar schema. SQLite `integrity_check=ok`, zero FK. Backup `data/backup-pre-cjf-tematico-20261013.sqlite` (481.345.536 bytes; SHA-256 `71f5338f921f49a41169ecf48d80e257bcb5a671b649cf9af6d6d3c3f890f012`). Sem envio à IpeaIA. Corpus de jurisprudência publicada é complementar, não amostra representativa nem autos integrais. Detalhes em `docs/FONTES_ABERTAS.md`. |
| 13/10/2026 | Avançar as pesquisas públicas seguintes de TNU/TRF2/TRF4/TRF5/TRF6 para `LOAS`, consultando URLs ainda não concluídas e mantendo cada tribunal separado. | 50 URLs TNU resultaram em 100 documentos novos; TRF2: 48/50; TRF4: 50/50; TRF5: 50/50; TRF6: 50/50; total 298 versões novas. 298/298 arquivos brutos gzip presentes e íntegros. Nenhum processo ou vínculo foi criado; corpus por fonte: TNU 266, TRF2 129, TRF4 132, TRF5 130, TRF6 135. Sem credencial, CAPTCHA, alteração de schema ou envio à IpeaIA; decisões são corpus complementar. |
| 13/10/2026 | Consultar mais 50 casos pendentes no PJe/TRF1 público, equilibrados entre Brasília, Formosa e Luziânia, sem login nem contorno de CAPTCHA, validando cada documento pelo CNJ do cabeçalho. | 50/50 consultas: 32 com documentos e 18 sem documentos-alvo; 67 documentos novos vinculados por CNJ explícito aos 32 processos. Distribuição 17/17/16; 218/218 arquivos brutos gzip íntegros; nenhum caso atingiu o limite de dez documentos. PJe total 590 documentos, população de processos inalterada. Estado final: 16.737 processos, 16.796 registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações, 2.515 documentos, 605 vínculos, zero extrações IA; `integrity_check=ok`, zero FK e duplicatas. Backup final `data/backup-pos-coletas-20261013.sqlite` (513.933.312 bytes; SHA-256 `8d0ffdd6b63232db7e509b34c8cee66a09f8190f41555cc965f8cb6aff110924`). Sem alteração de schema, chamada à IpeaIA ou commit/push. |
| 13/10/2026 | Avançar buscas públicas pendentes TNU/TRF2/TRF4/TRF5/TRF6 por `LOAS` e testar termo alternativo `BPC` no TRF6. | Novos documentos: TNU 80, TRF2 47, TRF4 50, TRF5 50, TRF6 100 (50 `LOAS` + 50 `BPC`), total +327? Correção: estes lotes somam 327 documentos nesta rodada incluindo a coleta de 100 no TRF6. Totais atuais: 2.853 documentos, 618 vínculos; TNU 346, TRF2 176, TRF4 182, TRF5 180, TRF6 235. Coleta pública complementar, sem processos ou vínculos presumidos; SQLite `integrity_check=ok`, zero violações FK. |
| 13/10/2026 | Suspender a segunda ampliação do PJe/TRF1 quando a validação de identidade documental encontrar divergência entre o CNJ consultado e o cabeçalho do documento. | Execução interrompida pela proteção existente após 15 processos tentados: 11 documentos novos preservados, uma divergência de identidade e os demais casos do lote não tentados. Sem contorno nem nova consulta. PJe total 601 documentos; banco 16.737 processos, 2.853 documentos, 618 vínculos, `integrity_check=ok`, zero violações FK. |
