# Coleta autônoma — 08/10/2026

Base explícita: `data/bpc-consolidado-luna-20261007.sqlite`.
Coletores existentes; sem alteração de schema, chamadas à IA, commit/push
ou atualização do pacote de transferência. CRPS permanece pendente conforme
`PENDENCIA_AUTOMACAO_CRPS.md`.

## Jurisprudência publicada

Cada busca usou `--query LOAS --limit 10 --timeout 25`, sem `--retentar`.
TNU e TRF5: oito páginas máximas; TRF2/TRF4/TRF6: seis.
TRFs: origem do próprio tribunal. Paginação segue somente links publicados.

| Fonte | URLs consultadas | Versões novas | Corpus antes | Corpus depois |
| --- | ---: | ---: | ---: | ---: |
| TNU | 10 | 19 | 38 | 57 |
| TRF2 | 10 | 10 | 24 | 34 |
| TRF4 | 10 | 10 | 22 | 32 |
| TRF5 | 10 | 10 | 21 | 31 |
| TRF6 | 10 | 10 | 27 | 37 |

Total documental: 173 → 232 versões, ganho de 59. TNU pode retornar vários
artigos por URL. Não são 59 processos novos nem amostra representativa.
As cinco buscas terminaram `concluida`, com Bronze original local.

Vínculos documentais: 4 → 6. Os dois novos são documentos TRF6 com CNJ
explícito coincidente com processos já existentes:
`1021302-15.2019.4.01.9999` e `1019783-05.2019.4.01.9999`.
Essa identidade não comprova residência DF/RIDE, pedido inicial ou mérito.
Nenhum processo novo foi criado; textos não foram enviados à IpeaIA.

## Comunica

Uma consulta diagnóstica sem retentativa para o primeiro CNJ ainda sem consulta
do manifesto de 400 retornou HTTP 503: `1002790-92.2021.4.01.3506`.
Não iniciei o lote nem alterei seu status no banco. Não é resultado vazio.
A sondagem foi transitória, não uma coleta Bronze/Silver. Permanecem 220
comunicações e 851 consultas; aguardar recuperação antes de retomar.

## INSS

Catálogo oficial consultado: último recurso publicado observado agosto/2026.
Ampliação retroativa para maio/2026, espécies 87/88, DF/GO/MG, com o coletor
de indeferimentos existente. Arquivo lido integralmente; apenas agregados
por UF/espécie/motivo persistidos. GO/MG reutilizam os mesmos bytes locais,
com conferência de recurso e competência pelo importador.

Cada importação leu 898.162 linhas integralmente:

| UF | Indeferimentos BPC selecionados | Agregados novos |
| --- | ---: | ---: |
| DF | 3.145 | 23 |
| GO | 5.165 | 19 |
| MG | 18.091 | 21 |

Total: 26.401 indeferimentos administrativos em 63 agregados novos. Não são
pessoas únicas nem processos judiciais. Cobertura passa de junho–agosto para
maio–agosto/2026 nas três UFs.

Concessões não foram ampliadas nesta rodada. Motivos administrativos agregados
não podem ser atribuídos a processos individuais.

## Verificação final

SQLite: `integrity_check = ok`, zero violações de chave estrangeira.
16.737 processos, 16.796 registros DataJud e 907.521 movimentos preservados.
232 versões documentais, seis vínculos, 220 comunicações, 851 consultas e
zero extrações IA. Os ganhos estão no banco local; o pacote já existente em
`transferencia/` ainda contém a versão anterior e não foi sobrescrito.
