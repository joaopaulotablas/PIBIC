# Coleta Comunica, diários e consulta PJe — 08/10/2026

## Síntese

O banco usado foi exclusivamente `data/bpc-consolidado-luna-20261007.sqlite`,
com `DATABASE_URL=sqlite:///data/bpc-consolidado-luna-20261007.sqlite`. Nenhuma
consulta ao PostgreSQL do `.env` foi feita. A seleção Comunica de 400 CNJs foi
salva antes da coleta, mas a API passou a responder HTTP 503 de forma contínua.
Interrompi após 10 CNJs e as cinco tentativas limitadas por CNJ, sem resultado
ou comunicação nova. Os outros 390 permanecem pendentes.

O acervo histórico oficial do TRF1 foi mapeado, mas os endereços de arquivo
publicados estavam indisponíveis ou com falha de certificado neste ambiente.
Nenhuma edição foi baixada; portanto não há publicação identificada nem
conclusão de ausência. A tela PJe respondeu sem autenticação, mas os testes não
confirmaram metadados de processo nem documentos públicos vinculáveis.

## Banco, backup e seleção Comunica

Antes da escrita, o banco tinha 16.737 processos, 16.796 registros DataJud,
907.521 movimentos, 220 comunicações, **841 consultas PJe**, 173
documentos públicos, quatro vínculos documentais e zero extrações IA. `PRAGMA
integrity_check` retornou `ok` e `PRAGMA foreign_key_check` não encontrou
violações. O backup consistente feito antes do lote é
`data/backup-pre-comunica-diarios-luna-20261008.sqlite` (459.776.000 bytes;
SHA-256 `98d86568bc326f4fe07d43e06349ba4928304ca06804754fd75a7145bb61a7c2`).
O arquivo não sobrescreve backup anterior.

Manifesto de seleção: `data/manifesto-comunica-luna-400-20261008.csv`, 400
CNJs, SHA-256 `21ad4ea9801501935817668a585dc36009e8d81670867d41efd92d23d47fd6fa`.
Semente `20261010`; `random.Random(seed + deslocamento_do_grupo)`, shuffle dos
estratos por ano de ajuizamento e assunto TPU, seguido de rodízio. Filtros:
TRF1, G1/JE, nível público (sigilo 0 ou ausente), assuntos 6114/11946/11947 e
código municipal cru do órgão julgador DataJud 743 (núcleo Brasília), 1798
(Formosa) ou 2788 (Luziânia). Residência não foi inferida. A seleção não é
aleatória simples nem representativa.

Para repetir a seleção no mesmo snapshot: agrupar CNJs distintos por grupo,
ano e família de assunto (prioridade 11946, 11947, 6114); ordenar a entrada por
CNJ/data DataJud/ID do registro/código do assunto; embaralhar cada estrato com
`random.Random(20261010 + deslocamento)`, em que Brasília=0, Formosa=1 e
Luziânia=2; percorrer as chaves ordenadas em rodízio até 200/100/100. Primeiro
excluir os três manifestos anteriores e as consultas `encontrado` ou
`sem_resultado`; validar unicidade dos 400 CNJs antes de gravar o CSV.

Dos 3.823 CNJs originais do recorte, foram excluídos todos os que já tinham
consulta `encontrado`/`sem_resultado` e os três manifestos anteriores; após
deduplicar a união dessas exclusões, restaram 3.135 elegíveis: 1.436 Brasília,
864 Formosa e 835 Luziânia. As quotas 200/100/100 foram preenchidas. No início
existiam 130 encontrados, 711 sem resultado e zero erros temporários nos 841
registros de consulta: não havia erro anterior para retentar.

Coleta nova `b6af7ba3ae05425389c52ea6128eb070`: encerrada como `falhou` após
indisponibilidade sustentada. Os 10 CNJs tentados pertencem a Formosa: um do
ano 2018 e nove de 2021. Cada um recebeu cinco respostas HTTP 503, totalizando
50 tentativas limitadas; nenhum bloqueio CAPTCHA, login ou HTTP 403 foi
repetido. A Bronze nova
`data/raw/comunica_pje/processos/2026-10-08/b6af7ba3-ae05-4253-89c5-2ea6128eb070.ndjson.gz`
foi preservada como parcial: 308 bytes, SHA-256
`ed790d41b254c7748e862f8a1c87507b814e35041e0802d35386b675cf321d49`, dez
linhas JSON válidas após descompressão parcial, sem trailer gzip. A coleta
ficou marcada `falhou`, com o caminho e a causa registrados. Não se conta essa
Bronze como íntegra.

| Grupo | Ano | Selecionados | Consultados | Encontrados | Vazios | Erros temporários | Pendentes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Formosa | 2018 | 1 | 1 | 0 | 0 | 1 | 0 |
| Formosa | 2021 | 36 | 9 | 0 | 0 | 9 | 27 |
| Formosa | 2022 | 34 | 0 | 0 | 0 | 0 | 34 |
| Formosa | 2023 | 29 | 0 | 0 | 0 | 0 | 29 |
| Luziânia | 2018 | 15 | 0 | 0 | 0 | 0 | 15 |
| Luziânia | 2019 | 1 | 0 | 0 | 0 | 0 | 1 |
| Luziânia | 2021 | 28 | 0 | 0 | 0 | 0 | 28 |
| Luziânia | 2022 | 28 | 0 | 0 | 0 | 0 | 28 |
| Luziânia | 2023 | 28 | 0 | 0 | 0 | 0 | 28 |
| Núcleo Brasília | 2019 | 40 | 0 | 0 | 0 | 0 | 40 |
| Núcleo Brasília | 2020 | 26 | 0 | 0 | 0 | 0 | 26 |
| Núcleo Brasília | 2021 | 39 | 0 | 0 | 0 | 0 | 39 |
| Núcleo Brasília | 2022 | 26 | 0 | 0 | 0 | 0 | 26 |
| Núcleo Brasília | 2023 | 19 | 0 | 0 | 0 | 0 | 19 |
| Núcleo Brasília | 2024 | 19 | 0 | 0 | 0 | 0 | 19 |
| Núcleo Brasília | 2025 | 26 | 0 | 0 | 0 | 0 | 26 |
| Núcleo Brasília | 2026 | 5 | 0 | 0 | 0 | 0 | 5 |
| **Total** |  | **400** | **10** | **0** | **0** | **10** | **390** |

Antes e depois: processos 16.737, comunicações 220, documentos 173, vínculos 4
e extrações IA 0 permaneceram iguais. Consultas PJe passaram de 841 para 851,
com dez novos status `erro_temporario`. Ganho líquido de comunicações e
documentos: zero; CNJs enriquecidos: zero. Nenhuma duplicação foi inserida.

## Piloto de diários históricos do TRF1/DF e GO

A [página oficial de Diários da Justiça do TRF1](https://www.trf1.jus.br/trf1/diarios-da-justica/diarios-da-justica)
respondeu HTTP 200. Ela separa: DJEN atual para atos judiciais; atos
administrativos desde 03/12/2020; e-DJF1 judicial de 20/03/2015 a 26/11/2020;
e-DJF1 de 05/10/2009 a 19/03/2015; e acervo de 1990–2008 encaminhado à
Biblioteca do Diário da Justiça. O caderno administrativo foi excluído do
piloto e o DJEN atual não foi tratado como arquivo histórico.

Foram selecionados 30 CNJs antigos sem comunicação no banco, por data de
ajuizamento crescente e grupo do órgão julgador (15 Brasília, oito Formosa,
sete Luziânia). Manifesto local:
`data/piloto-diarios-trf1-cnjs-luna-20261008.csv`, SHA-256
`71ae777c93be86a25bef9916ef72180b18f43e5096a6959d35bd0a61bd936b06`. Tem
datas de ajuizamento e movimentos observados para orientar, sem presumir que
qualquer data de movimento seja a data da publicação. Anos de ajuizamento:
Brasília 2009, 2013, 2017–2018; Formosa 2011–2012 e 2015–2017; Luziânia
2008–2010.

O link oficial publicado para o e-DJF1 2015–2020 (`https://edj.trf1.jus.br/edj/`)
falhou em resolução DNS local; a consulta web recebeu 502. O link oficial do
acervo 2009–2015
(`https://portal.trf1.jus.br/dspace/handle/123/163457`) retornou HTTP 500; a
ferramenta web expirou por timeout. O link oficial 1990–2008 aponta para
`https://biblioteca.in.gov.br/es/diario-oficial-da-uniao`; a conexão Python
falhou na validação da cadeia TLS. Não ignorei a validação TLS. A página não
ofereceu, nesta tentativa, mecanismo de pesquisa judicial utilizável para
consultar até 20 edições. Resultado do piloto: zero edições selecionadas,
zero consultadas, zero arquivos baixados. Não há hash de edição, página ou
extração PDF a declarar. A conclusão é indisponibilidade do acesso neste
ambiente, não ausência de publicação nos diários. Uma consulta anterior
registrada em `RELATORIO_EXECUCAO_COLETA_LUNA.md` encontrou PDF do e-DJF1 de
14/02/2022 sem atos judiciais a divulgar; isso não identifica qualquer dos 30
processos deste piloto.

Como nenhum documento de diário foi obtido ou vinculado, não houve extração de
texto, OCR, inclusão em `documentos_publicos` ou alteração de schema. Para
retomar, o pesquisador precisa fornecer/validar um acesso oficial funcional ao
acervo judicial e selecionar edições a partir dos períodos dos 30 processos;
somente links publicados devem ser seguidos. Imagens sem texto ficam pendentes
de OCR, e CNJ citado como precedente não cria vínculo.

## Viabilidade da consulta pública PJe/TRF1

Endpoint testado:
`https://pje1g-consultapublica.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam`.
A página inicial respondeu HTTP 200 no host oficial, sem redirecionamento e
sem login. O formulário JSF contém busca por numeração única. Foram submetidos
cinco CNJs existentes da base pela consulta pública normal; os cinco POSTs
retornaram HTTP 200. Em quatro respostas inspecionáveis o CNJ informado foi
refletido, mas não houve linhas de resultado nem links de documento detectados.
A primeira resposta continha o script hCaptcha, sem desafio apresentado; não
foi executado nem resolvido CAPTCHA. Não houve 403, autenticação solicitada ou
redirecionamento para host terceiro.

Resultado: a busca sem login foi acessível, mas não se confirmou disponibilidade
de metadados retornados, documentos públicos, identidade do processo pelo
resultado ou identidade de qualquer documento. Um número refletido no formulário
não comprova que o processo foi localizado. O acesso não demonstra autos
completos. A própria página alerta que processo sigiloso ou dado incorreto pode
não retornar resultado. A consulta não gravou dados no banco.

## CRPS — orientação para o pesquisador

A página oficial [Consulta Jurisprudência do CRPS](https://www.gov.br/previdencia/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/conselho-de-recursos-da-previdencia-social/consulta-jurisprudencia)
descreve decisões administrativas e filtros por tipo de processo, unidade
julgadora, objeto do recurso, tipo/espécie de benefício e palavras na ementa ou
voto. O portal exige conta gov.br. O pesquisador deve acessar diretamente pelo
link oficial com sua própria conta, sem compartilhar senha, token ou sessão;
consultar espécie 87/88 e termos relacionados a concessão, indeferimento,
revisão, cessação e restabelecimento; guardar identificador, data, unidade,
espécie, decisão e arquivo oficial com hash para análise administrativa.
Esse corpus pode ajudar a construir categorias de motivo administrativo, mas
nenhum motivo pode ser atribuído a um processo BPC sem evidência individual e
vínculo explícito.

## Revisão local de textos Comunica

Não houve texto novo para revisar na coleta interrompida. Reutilizei a revisão
local dos dez atos publicados já examinados, agora com manifesto enriquecido
`data/revisao_comunicacoes_manifesto_luna_diarios_20261008.csv` (SHA-256
`48031509cc963458e9a45be9e2e85992a97d433017363a04517a8938fad6d3c4`). Cada
linha contém CNJ, ID local, ID de origem Comunica, hash, tipo publicado,
critério e conclusão; a página é declarada não aplicável por não ser PDF. O
manifesto não inclui nomes, CPF ou trechos pessoais e deve continuar local.

Seis textos eram sentenças e quatro decisões. Fundamentação foi identificada
em 10/10; dispositivo ou providência em 10/10; motivo administrativo explícito
de negativa em 0/10. Em cinco, a judicialização foi mandado de segurança por
demora administrativa, sem decisão do pedido inicial de BPC; um tratou de
implantação de benefício já concedido administrativamente em recurso; quatro
eram atos processuais incidentais. Esses eixos foram mantidos separados:
motivo da judicialização não equivale a motivo da negativa, e providência ou
extinção processual não equivale a resultado de mérito do pedido inicial.

## Retomada da amostra Comunica — 13/10/2026

A API pública voltou a responder normalmente. Os 400 CNJs do manifesto foram
consultados sem autenticação: 200 do núcleo Brasília, 100 de Formosa e 100 de
Luziânia. Resultado final: 41 CNJs com publicações e 359 `sem_resultado`;
distribuição por grupo: Brasília 31/200, Formosa 4/100 e Luziânia 6/100. Foram
acrescentadas 82 comunicações distintas, elevando o total local de 220 para
302 e as consultas PJe de 851 para 1.241. `sem_resultado` refere-se somente à
resposta do Comunica, não prova que não existam atos nos autos ou em outras
fontes.

A execução principal `3d7d4697989a4339ae5f1077c27676f0` consultou 389 CNJs e
registrou 77 comunicações; seu Bronze
`data/raw/comunica_pje/processos/2026-10-13/3d7d4697-989a-4339-ae5f-1077c27676f0.ndjson.gz`
foi descompactado integralmente, com 389 linhas NDJSON, SHA-256
`b1e59dfc738d7057d728c903bb3644ef76e707ae6934458e5619e26d3a4a45b4`. Os dez
CNJs consultados no lote anterior acrescentaram cinco comunicações; mais um
CNJ foi testado separadamente e não teve resultado. A soma é 400 consultas e
82 itens novos. Uma invocação intermediária falhou antes de chamar a API porque
o PowerShell juntou a lista de CNJs em um único argumento; ficou registrada
como coleta `falhou`, zero registros, sem efeito sobre os dados. A invocação
seguinte passou os números individualmente e concluiu o restante.

Foi criado antes da escrita o backup consistente
`data/backup-pre-comunica-djen-20261012.sqlite`, 480.641.024 bytes, SHA-256
`3a8a25d99350defd1b0f766939f0758ae5c520505c9e69234cabc28f51d5aea`; o backup
passou `integrity_check=ok`. Após a coleta, SQLite: 16.737 processos, 16.796
registros DataJud, 907.521 movimentos, 1.241 consultas PJe, 302 comunicações,
1.058 documentos, 531 vínculos e zero extrações IA. O banco passou
`integrity_check=ok`, `foreign_key_check` retornou zero violações e não há
duplicatas na chave processo + hash de comunicação. A Bronze principal foi
verificada como gzip completo. Não houve alteração de schema, chamada à
IpeaIA, criação/sobrescrita de pacote de transferência ou commit/push. Os
manifestos e dados brutos permanecem locais em `data/`.

A fonte acrescenta textos de publicações/intimações onde disponíveis, não
petições ou inteiro teor universal dos autos. A coleta não altera essa
limitação nem autoriza inferir residência a partir do órgão julgador.

## Ampliação temática CJF/JEF1 — 13/10/2026

Depois da retomada Comunica, testei a pesquisa temática pública do
[CJF/JEF1](https://jurisprudencia.cjf.jus.br/trf1/index.xhtml), distinta da
consulta por CNJ. A busca `BPC` reportou 1.092 resultados em 37 páginas. O
coletor passou a aceitar `--pagina-inicial` para retomar faixas de páginas sem
recomeçar sempre da primeira. Foram consultadas todas as páginas e persistidos
1.092 acórdãos com texto e CNJ explícito na fonte `cjf_trf1`, sem chaves
duplicadas. 42 arquivos HTML/XML gzip foram descompactados integralmente; os
dados ficam em `data/raw/cjf_trf1/`, fora do Git.

Sete documentos ficaram ligados a seis processos já existentes, exclusivamente
por CNJ explícito; nenhum processo foi criado. O total da fonte CJF passou a
1.104 versões (1.100 IDs documentais distintos, com versões preservadas), e o
texto da coleta de hoje soma 6.814.222 caracteres. A busca inclui decisões
publicadas, não é representativa de toda a litigância BPC e não fornece os autos
integrais de cada CNJ.

Backup anterior às coletas CJF:
`data/backup-pre-cjf-tematico-20261013.sqlite`, 481.345.536 bytes, SHA-256
`71f5338f921f49a41169ecf48d80e257bcb5a671b649cf9af6d6d3c3f890f012`,
`integrity_check=ok`.

## Expansão de outros tribunais e PJe/TRF1 — 13/10/2026

Continuei nas fontes oficiais acessíveis sem credenciais. Nas pesquisas `LOAS`
de resultados seguintes, a TNU consultou 50 URLs e persistiu 100 documentos;
TRF2 consultou 50 e persistiu 48; TRF4, TRF5 e TRF6 consultaram 50 cada e
persistiram 50 cada. São 298 versões novas no corpus suplementar. Os totais por
fonte ficaram TNU 266, TRF2 129, TRF4 132, TRF5 130 e TRF6 135 documentos. Os
298 arquivos brutos novos foram verificados como gzip íntegros. Nenhum deles
criou processo ou vínculo para a amostra.

Também consultei 50 CNJs ainda pendentes na consulta pública PJe/TRF1, com
rodízio entre Brasília (17), Formosa (17) e Luziânia (16). O portal não pediu
login ou CAPTCHA. Em 32 processos foram encontrados textos; 18 consultas não
tinham documento-alvo público. Persisti 67 documentos com CNJ confirmado no
cabeçalho, ligados aos 32 processos. Os 218 arquivos brutos HTML gzip do lote
estão íntegros. Nenhum processo ultrapassou o limite de dez documentos. A
consulta limita-se à página pública e não representa autos integrais.

Estado final do SQLite: 16.737 processos, 16.796 registros DataJud, 907.521
movimentos, 1.241 consultas PJe, 302 comunicações, 2.515 documentos, 605
vínculos e zero extrações IA. `integrity_check=ok`, zero violações FK, zero
duplicatas em processo/hash de comunicação e zero duplicatas em
fonte/documento/hash. Nenhuma chamada à IpeaIA ou alteração de schema.

Snapshot final restaurável: `data/backup-pos-coletas-20261013.sqlite`,
513.933.312 bytes, SHA-256
`8d0ffdd6b63232db7e509b34c8cee66a09f8190f41555cc965f8cb6aff110924`; o arquivo
também passou `integrity_check=ok` e `foreign_key_check` sem violações. Os
dados e brutos permanecem locais, fora do Git; não houve commit/push nem
atualização do banco remoto.

Comunica contém publicações, CJF/TNU/TRFs são jurisprudência suplementar e PJe
contém apenas documentos disponibilizados publicamente. Essas fontes melhoram
o corpus textual, mas não fornecem universalmente as peças nem o inteiro teor
dos processos da amostra; nenhum texto foi enviado à IpeaIA.
