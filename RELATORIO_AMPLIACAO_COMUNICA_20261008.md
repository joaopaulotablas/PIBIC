# Relatório de ampliação Comunica PJe — 08/10/2026

## Escopo e método

Banco trabalhado: `data/bpc-consolidado-luna-20261007.sqlite` (SQLite selecionado explicitamente em todas as execuções por `DATABASE_URL=sqlite:///data/bpc-consolidado-luna-20261007.sqlite`). A coleta não criou processos. O escopo é Comunica PJe por CNJ, uma API pública paginada de comunicações publicadas; não é API de autos nem garante inteiro teor.

O backup anterior ao lote, `data/backup-pre-comunica-20261008.sqlite`, foi conferido com 16.737 processos, 16.796 registros DataJud, 907.521 movimentos, 168 documentos públicos, 4 vínculos documentais, 0 extrações IA e 110 comunicações. Um novo backup consistente, `data/backup-pre-comunica-luna-20261008.sqlite`, foi feito pela API `sqlite3.Connection.backup()` antes da retomada, quando havia 151 comunicações. Nenhum backup anterior foi sobrescrito.

Manifestos locais, ambos com 200 CNJs únicos e quotas 100/50/50:

- `data/manifesto-comunica-200-20261008.csv` — seed `20261008`; seleção estratificada por ano e combinação de assunto, com rodízio; a origem foi um manifesto candidato de 2.000 casos após excluir consultas anteriores. Não é amostra aleatória simples nem representativa dos 3.823 CNJs candidatos do recorte. SHA-256: `aed1e21ab92863bf34dc222eefa4b84de4f63290af4deff3b569fd8c0212b4b1`.
- `data/manifesto-comunica-200b-20261008.csv` — seed `20261009`; entre os 3.823 candidatos originais, excluíram-se CNJs já presentes em `consultas_pje` e os do primeiro manifesto. Restaram 3.335 elegíveis (1.536 núcleo DF, 914 Formosa e 885 Luziânia). Em cada grupo, `random.Random(20261009)` embaralhou estratos ano/assunto e a seleção percorreu os estratos em rodízio. Os 200 CNJs selecionados não se repetem entre grupos ou lotes. A quota foi preenchida integralmente. SHA-256: `a5cb483e02a9ff8810e34e8991f27be33decbeb8dbb407a29eb3be8b5ab452db`.

O primeiro manifesto já tinha 136 consultas no início (30 `encontrado`, 106 `sem_resultado`); consultei somente os 64 pendentes. Não houve repetição de resultados concluídos/vazios. Depois da persistência correta e sem bloqueio, gerei o segundo manifesto antes de consultar seus 200 CNJs inéditos.

IDs de coleta Comunica relacionados a esta ampliação:

- `8ed0515fabfb45b89671e6768f730c02`: execução interrompida previamente; ficou `falhou`, com 41 comunicações registradas. Preservei o status. O arquivo Bronze registrado existe, mas a leitura termina em `EOFError` antes do trailer gzip; não o corrigi nem inventei itens.
- `03e5da5c5f8e4ac08724a93fc65aeb7e`: conclusão dos 64 pendentes; 64 linhas JSON Bronze válidas, 11 comunicações observadas e persistidas como novas.
- `b69129b8053840219f9841183ffa1cc0`: segundo lote concluído; 200 linhas JSON Bronze válidas, 58 comunicações observadas e persistidas como novas.

O cliente `ComunicaPjeClient` manteve paginação, intervalo mínimo de 1 segundo, limite existente de até cinco tentativas para falhas temporárias e sem paralelismo. Todas as consultas destes dois lotes receberam HTTP 200; não ocorreu CAPTCHA, 403 ou bloqueio. Não houve erro final nem CNJ pendente ao encerrar.

## Resultados por lote, grupo e ano

`Observadas` — a soma dos itens retornados pela API por consulta. `Novas` deduplica contra o backup anterior ao lote pela chave contratual `processo_id + hash_conteudo` (comparada pelo CNJ entre arquivos). `Encontrados` e `Vazios` contam CNJs. `Erros` e `Pendentes` ficam separados.

### Totais por lote e grupo

| Lote | Grupo | Selecionados | Consultados | Encontrados | Vazios | Erros | Pendentes | Comunicações observadas | Novas líquidas |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Lote 1 — manifesto original | Núcleo TRF1/DF (código local DataJud 743) | 100 | 100 | 25 | 75 | 0 | 0 | 33 | 33 |
| Lote 1 — manifesto original | Formosa (código local DataJud 1798) | 50 | 50 | 5 | 45 | 0 | 0 | 8 | 8 |
| Lote 1 — manifesto original | Luziânia (código local DataJud 2788) | 50 | 50 | 7 | 43 | 0 | 0 | 11 | 11 |
| Lote 2 — manifesto adicional | Núcleo TRF1/DF (código local DataJud 743) | 100 | 100 | 24 | 76 | 0 | 0 | 40 | 40 |
| Lote 2 — manifesto adicional | Formosa (código local DataJud 1798) | 50 | 50 | 2 | 48 | 0 | 0 | 7 | 7 |
| Lote 2 — manifesto adicional | Luziânia (código local DataJud 2788) | 50 | 50 | 5 | 45 | 0 | 0 | 11 | 11 |

### Detalhamento anual

Cada linha mantém o ano de ajuizamento do manifesto. Uma quota anual muito pequena ou ausente em grupo é consequência da disponibilidade do estrato e do rodízio, não de filtro por recência.

| Lote | Grupo | Ano | Selecionados | Consultados | Encontrados | Vazios | Erros | Pendentes | Observadas | Novas líquidas |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Lote 1 | Formosa (código local DataJud 1798) | 2017 | 3 | 3 | 0 | 3 | 0 | 0 | 0 | 0 |
| Lote 1 | Formosa (código local DataJud 1798) | 2018 | 6 | 6 | 0 | 6 | 0 | 0 | 0 | 0 |
| Lote 1 | Formosa (código local DataJud 1798) | 2019 | 5 | 5 | 0 | 5 | 0 | 0 | 0 | 0 |
| Lote 1 | Formosa (código local DataJud 1798) | 2020 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| Lote 1 | Formosa (código local DataJud 1798) | 2021 | 10 | 10 | 0 | 10 | 0 | 0 | 0 | 0 |
| Lote 1 | Formosa (código local DataJud 1798) | 2022 | 10 | 10 | 0 | 10 | 0 | 0 | 0 | 0 |
| Lote 1 | Formosa (código local DataJud 1798) | 2023 | 9 | 9 | 0 | 9 | 0 | 0 | 0 | 0 |
| Lote 1 | Formosa (código local DataJud 1798) | 2024 | 1 | 1 | 1 | 0 | 0 | 0 | 3 | 3 |
| Lote 1 | Formosa (código local DataJud 1798) | 2025 | 3 | 3 | 2 | 1 | 0 | 0 | 2 | 2 |
| Lote 1 | Formosa (código local DataJud 1798) | 2026 | 2 | 2 | 2 | 0 | 0 | 0 | 3 | 3 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2008 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2015 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2016 | 4 | 4 | 3 | 1 | 0 | 0 | 3 | 3 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2017 | 4 | 4 | 0 | 4 | 0 | 0 | 0 | 0 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2018 | 5 | 5 | 0 | 5 | 0 | 0 | 0 | 0 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2019 | 7 | 7 | 0 | 7 | 0 | 0 | 0 | 0 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2020 | 2 | 2 | 0 | 2 | 0 | 0 | 0 | 0 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2021 | 10 | 10 | 0 | 10 | 0 | 0 | 0 | 0 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2022 | 7 | 7 | 0 | 7 | 0 | 0 | 0 | 0 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2023 | 6 | 6 | 3 | 3 | 0 | 0 | 6 | 6 |
| Lote 1 | Luziânia (código local DataJud 2788) | 2025 | 3 | 3 | 1 | 2 | 0 | 0 | 2 | 2 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2018 | 7 | 7 | 0 | 7 | 0 | 0 | 0 | 0 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2019 | 12 | 12 | 0 | 12 | 0 | 0 | 0 | 0 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2020 | 13 | 13 | 2 | 11 | 0 | 0 | 3 | 3 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2021 | 13 | 13 | 0 | 13 | 0 | 0 | 0 | 0 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2022 | 12 | 12 | 1 | 11 | 0 | 0 | 1 | 1 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2023 | 12 | 12 | 3 | 9 | 0 | 0 | 4 | 4 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2024 | 6 | 6 | 3 | 3 | 0 | 0 | 3 | 3 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2025 | 13 | 13 | 5 | 8 | 0 | 0 | 7 | 7 |
| Lote 1 | Núcleo TRF1/DF (código local DataJud 743) | 2026 | 12 | 12 | 11 | 1 | 0 | 0 | 15 | 15 |
| Lote 2 | Formosa (código local DataJud 1798) | 2018 | 7 | 7 | 0 | 7 | 0 | 0 | 0 | 0 |
| Lote 2 | Formosa (código local DataJud 1798) | 2019 | 5 | 5 | 0 | 5 | 0 | 0 | 0 | 0 |
| Lote 2 | Formosa (código local DataJud 1798) | 2021 | 14 | 14 | 1 | 13 | 0 | 0 | 2 | 2 |
| Lote 2 | Formosa (código local DataJud 1798) | 2022 | 12 | 12 | 1 | 11 | 0 | 0 | 5 | 5 |
| Lote 2 | Formosa (código local DataJud 1798) | 2023 | 12 | 12 | 0 | 12 | 0 | 0 | 0 | 0 |
| Lote 2 | Luziânia (código local DataJud 2788) | 2016 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 |
| Lote 2 | Luziânia (código local DataJud 2788) | 2017 | 3 | 3 | 0 | 3 | 0 | 0 | 0 | 0 |
| Lote 2 | Luziânia (código local DataJud 2788) | 2018 | 6 | 6 | 1 | 5 | 0 | 0 | 1 | 1 |
| Lote 2 | Luziânia (código local DataJud 2788) | 2019 | 6 | 6 | 0 | 6 | 0 | 0 | 0 | 0 |
| Lote 2 | Luziânia (código local DataJud 2788) | 2021 | 11 | 11 | 0 | 11 | 0 | 0 | 0 | 0 |
| Lote 2 | Luziânia (código local DataJud 2788) | 2022 | 10 | 10 | 0 | 10 | 0 | 0 | 0 | 0 |
| Lote 2 | Luziânia (código local DataJud 2788) | 2023 | 10 | 10 | 1 | 9 | 0 | 0 | 1 | 1 |
| Lote 2 | Luziânia (código local DataJud 2788) | 2025 | 3 | 3 | 3 | 0 | 0 | 0 | 9 | 9 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2018 | 5 | 5 | 0 | 5 | 0 | 0 | 0 | 0 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2019 | 14 | 14 | 1 | 13 | 0 | 0 | 2 | 2 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2020 | 14 | 14 | 2 | 12 | 0 | 0 | 2 | 2 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2021 | 14 | 14 | 0 | 14 | 0 | 0 | 0 | 0 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2022 | 13 | 13 | 0 | 13 | 0 | 0 | 0 | 0 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2023 | 10 | 10 | 2 | 8 | 0 | 0 | 4 | 4 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2024 | 6 | 6 | 2 | 4 | 0 | 0 | 6 | 6 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2025 | 12 | 12 | 6 | 6 | 0 | 0 | 14 | 14 |
| Lote 2 | Núcleo TRF1/DF (código local DataJud 743) | 2026 | 12 | 12 | 11 | 1 | 0 | 0 | 12 | 12 |

## Publicações com rótulo formal e revisão local

Nos 400 CNJs dos dois manifestos, 10 CNJs distintos têm ao menos uma comunicação cujo tipo publicado contém rótulo de sentença, decisão ou acórdão. Há 7 CNJs com rótulo de sentença (6 `Sentença Tipo C`, 1 `Sentença Tipo A`), 4 com rótulo de decisão (3 `Decisão`, 1 `Decisão Monocrática Terminativa`) e nenhum com rótulo de acórdão; um CNJ aparece nas famílias sentença e decisão, por isso a união é 10. São rótulos publicados, não classificação do mérito.

Revisei localmente 10 textos novos com esses rótulos, sem reproduzir nomes, CPF ou trechos pessoais neste relatório: 6 sentenças e 4 decisões. Os seis textos de sentença trazem razões e uma conclusão/ordem; cinco são mandados de segurança relacionados à demora administrativa ou à implantação de benefício e terminam sem julgamento do direito inicial ao BPC. O outro texto trata da implantação de benefício já concedido administrativamente em recurso. As quatro decisões trazem razões ou contexto processual e uma providência, como instrução, redistribuição ou cumprimento; não decidem o pedido inicial de concessão. Rótulo e conteúdo foram conferidos separadamente.

Motivo explícito para indeferimento administrativo do BPC: **0/10 textos revisados**. Alguns descrevem demora, pedido ainda não analisado ou cumprimento de concessão administrativa; isso não revela o fundamento de uma negativa. Não inferi motivos ausentes.

## Ganho e limites

O total no banco subiu de 110 para 220 comunicações, ganho líquido de **110**: 52 associadas ao primeiro manifesto (41 já registradas na coleta interrompida e 11 na conclusão dos 64 pendentes) e 58 no segundo. As 110 observações da API coincidiram com 110 chaves novas após deduplicação; nenhum item duplicado foi contado como ganho. Os 400 CNJs são distintos; 68 tiveram publicação encontrada (37 no primeiro e 31 no segundo lote), e 332 ficaram sem resultado nesta consulta. Cada linha em `comunicacoes_pje` é publicação, não processo.

O ganho permite revisar alguns atos processuais publicados, inclusive despachos e sentenças em mandados de segurança sobre demora administrativa. Não dá acesso às peças completas, aos requerimentos administrativos ou a uma série completa de decisões; portanto não basta para explicar toda a judicialização, a motivação das negativas ou a procedência dos pedidos. `Sem resultado` significa somente que a API não retornou publicação para aquele CNJ durante a consulta.

A amostra foi selecionada em pool de candidatos por assunto CNJ e sede do órgão julgador: núcleo TRF1/DF (743), Formosa (1798) e Luziânia (2788). Os códigos de Formosa/Luziânia e o de Brasília identificam órgão julgador, não residência. O grupo é limitado a esses locais TRF1; não inclui todos os municípios da RIDE, Unaí/TRF6 ou tribunais estaduais. Há estratos entre 2008 e 2026, porém a chance de publicação varia com o tempo e com a composição por assunto. A seleção não é aleatória simples nem representativa; não extrapolar taxas à população dos 3.823 candidatos ou ao conjunto de requerentes.

## Integridade, preservação e Bronze

| Verificação | Antes (backup `backup-pre-comunica-20261008.sqlite`) | Final |
|---|---:|---:|
| Processos | 16.737 | 16.737 |
| Registros DataJud | 16.796 | 16.796 |
| Movimentos | 907.521 | 907.521 |
| Documentos públicos | 168 | 168 |
| Vínculos documentais | 4 | 4 |
| Extrações IA | 0 | 0 |
| Comunicações | 110 | 220 |
| Consultas PJe | 441 | 841 |

`PRAGMA integrity_check`: `ok`. `PRAGMA foreign_key_check`: zero linhas. Nenhum processo, registro DataJud, movimento, documento público, vínculo documental ou extração IA foi alterado pela ampliação. Não houve edição de schema. Os gzip das duas coletas concluídas foram lidos integralmente e continham 64 e 200 linhas JSON válidas. O Bronze de `8ed0515fabfb45b89671e6768f730c02` existe, foi preservado, mas está truncado; sua ausência de trailer não foi mascarada. O registro da coleta DataJud `c165d92b6b0d486ba4d17193ee62d73e` permaneceu `executando` no snapshot; não havia processo local de coleta DataJud/Comunica em execução e o registro foi mantido sem alteração.

## Retomada se uma consulta ficar incompleta

Execute na raiz do projeto. O bloco lê o manifesto selecionado, não repete `encontrado`/`sem_resultado`, consulta CNJs ainda sem `consultas_pje` e permite uma única rodada adicional para `erro_temporario` somente quando a tentativa anterior ficou abaixo do limite 5 do cliente. Bloqueios, erros permanentes e erros temporários já no limite são listados à parte e não consultados automaticamente.

```powershell
$env:DATABASE_URL = 'sqlite:///data/bpc-consolidado-luna-20261007.sqlite'
$env:PYTHONPATH = 'ingestion/src'
$env:COMUNICA_MANIFEST = 'data/manifesto-comunica-200b-20261008.csv'
$code = @"
import csv, json, os, sqlite3
from pathlib import Path
p=Path('data/bpc-consolidado-luna-20261007.sqlite').resolve()
c=sqlite3.connect(f'file:{p}?mode=ro',uri=True)
state={n:(st,a or 0) for n,st,a in c.execute('select p.numero_processo,q.status,q.tentativas from processos p left join consultas_pje q on q.processo_id=p.id')}
rows=list(csv.DictReader(open(os.environ['COMUNICA_MANIFEST'],encoding='utf-8-sig',newline='')))
pending=[x['cnj'] for x in rows if (state.get(x['cnj'],(None,0))[0] is None or state[x['cnj']][0]=='erro_temporario' and state[x['cnj']][1]<5)]
errors=[(x['cnj'],state[x['cnj']][0],state[x['cnj']][1]) for x in rows if x['cnj'] in state and state[x['cnj']][0] is not None and state[x['cnj']][0] not in ('encontrado','sem_resultado') and not (state[x['cnj']][0]=='erro_temporario' and state[x['cnj']][1]<5)]
print(json.dumps({'pending':pending,'errors':errors}))
"@
$resultJson = $code | .\.venv\Scripts\python.exe -
if ($LASTEXITCODE -ne 0) { throw 'Falha ao filtrar o manifesto no SQLite' }
$selection = $resultJson | ConvertFrom-Json
Write-Output "Pending CNJs: $($selection.pending.Count); errors or blocks to review: $($selection.errors.Count)"
if ($selection.errors.Count -gt 0) { $selection.errors | ConvertTo-Json -Compress }
if ($selection.pending.Count -gt 0) { .\.venv\Scripts\python.exe -m bpc_ingestion comunica --numero $selection.pending --interval 1 }
```

## Complemento de rastreabilidade, recuperacao e transferencia — 08/10/2026

### Revisao textual rastreavel

Reavaliei dez textos publicados e registrei os resultados no manifesto local
`data/revisao_comunicacoes_manifesto_20261008.csv`, ignorado pelo Git. Cada linha
contem CNJ, ID Comunica, hash_conteudo, rotulo publicado, criterio, conclusao,
e os tres indicadores pedidos. Nao contem nomes, CPF ou citacoes pessoais.
Foram seis sentencas e quatro decisoes; uma publicacao de decisao compartilha
CNJ com uma sentenca. Fundamentacao: 10/10; dispositivo/providencia: 10/10;
motivo explicito de negativa administrativa: 0/10. Cinco sentencas tratam de
mora/ordem de analise e extinguem o mandado sem resolver o direito inicial ao
BPC; outra extingue por perda superveniente do objeto apos andamento do pedido.
Uma sentenca confirma seguranca para implantacao de beneficio ja concedido
administrativamente em recurso. As decisoes restantes tratam de emenda da
inicial, instrucao, cumprimento ou competencia. Rotulo, motivo da judicializacao,
negativa administrativa e resultado judicial foram conferidos separadamente.

### Gzip truncado e recuperacao

O arquivo original da coleta `8ed0515fabfb45b89671e6768f730c02` foi preservado
sem qualquer escrita (28.449 bytes; SHA-256
`8983c1a9133a5fd47d95bb4b00ee8088c10f274b231ffac44f0709d99427f6a5`). Ele nao
possui trailer/CRC verificavel. A leitura recuperou 136 linhas JSON completas,
30 com status encontrado e 106 sem_resultado, todas HTTP 200. As outras 64
consultas do manifesto ja possuem Bronze integra em coletas concluidas. Assim,
os 136 CNJs, e somente eles, foram reconsultados: a lista exata e o status
anterior constam em `data/recuperacao-bronze-comunica-8ed0515f-20261008.csv`.

Nova coleta `28a0d9a73da5405f833f2acb1dc49334` concluiu com 136 linhas gzip
validas, 30 encontradas, 106 sem resultado, zero erros e zero bloqueios. Foram
observadas 41 comunicacoes, todas deduplicadas contra o banco pela chave
processo + hash; entraram zero novas, mantendo 220. Esta consulta atual nao
reconstroi necessariamente a resposta historica original. Nao houve retry de
bloqueios nem contorno de CAPTCHA. O arquivo antigo continua no local original.

### Modo local de analise textual

Atualizei primeiro `docs/CONTRATOS.md` com `tipo_extracao=comunicacao_bpc_texto`,
prompt proprio `ipeaia_comunicacoes_v1`, evidencias por comunicacao_id/hash/trecho,
campos separados, classificacoes permitidas e status pendente. O codigo acrescenta
`ipeaia-comunicacoes-preparar` e `ipeaia-comunicacoes-importar`; ambos sao locais
e nao chamam rede. A pre-visualizacao preparada em
`data/ipeaia_comunicacoes_preparadas.json` contem 20 comunicacoes de 7 processos,
25.257 caracteres minimizados, sem CNJ, CPF, email ou URL detectados por
validacao automatica. O modo rejeita evidencias sem vinculo, hash ou trecho na
entrada e insere extracoes novas sem atualizar as anteriores. O arquivo segue
com revisao de privacidade pendente; nao enviei texto a IpeaIA e nao criei
resultado artificial, portanto `extracoes_ia` permanece com zero linhas.

Testes novos em `ingestion/tests/test_communication_analysis.py`: 5 passaram,
cobrindo minimizacao, limites, vinculo ID/hash/trecho ao texto publicado,
ausencia de evidencia e preservacao de extracoes existentes. Suite completa: 139 passaram (dois avisos
de depreciacao do Starlette/httpx).

### Pacote SQLite atualizado

Gerei `transferencia/bpc-consolidado-luna-20261008.sqlite.gz` a partir de
`data/bpc-consolidado-luna-20261007.sqlite`, selecionado explicitamente por
`DATABASE_URL=sqlite:///data/bpc-consolidado-luna-20261007.sqlite`. Nao usei o
PostgreSQL do `.env`. Backup SQLite consistente: `data/backup-pre-transferencia-luna-20261008.sqlite`.
O pacote tem 19 tabelas e SHA-256
`b22e9de6974cc0fe78056e1e669be6b1a2ff3f7b39181eae0d57950b494e9113`. Contagens:
16.737 processos; 16.796 registros DataJud; 907.521 movimentos; 220 comunicacoes;
841 consultas PJe; 168 documentos publicos; 4 vinculos documentais; zero
extracoes IA. A copia de teste descompactada teve as 19 contagens identicas,
`integrity_check=ok` e zero violacoes FK. O pacote nao contem arquivos Bronze,
logs ou diagnosticos.

O guia sem Docker esta em `GUIA_TRANSFERENCIA_BPC_CONSOLIDADO.md`. Antes de
qualquer troca no servidor remoto, faca snapshot do SQLite remoto pela API de
backup, confira `extracoes_ia` e, se necessario, consolide snapshot primeiro e
pacote depois para um destino novo. Revise conflitos, FKs, evidencias e
conteudos antes de selecionar a saida; nao sobrescreva nem descarte extracoes
remotas.

### Entrega e pendencias

Pronto para transferencia controlada: o pacote SQLite com o SHA-256 acima e o
guia de instalacao. O banco contem textos publicados que podem conter dados
pessoais e exige revisao de privacidade antes de publicacao aberta. O manifesto
local de revisao inclui CNJ/IDs/hashes conforme pedido e tambem deve passar por
revisao antes de publicacao. A pre-visualizacao minimizada exige revisao humana
antes de qualquer envio posterior. Nenhum Bronze ou diagnostico foi adicionado
ao Git; os pacotes/manifestos sensiveis sao ignorados. Nao fiz commit ou push e
nao alterei o submodulo `jeferson/bpc-loas`.
