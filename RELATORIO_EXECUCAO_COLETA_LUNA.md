# Relatório de execução da coleta Luna

**Data:** 07/10/2026  
**Base de trabalho:** `data/bpc-consolidado-luna-20261007.sqlite`  
**Situação:** execução local; origens preservadas e não promovida à base do pesquisador.

## Revisão e correções — 08/10/2026

A revisão independente confirmou os totais da base consolidada, integridade
SQLite `ok`, ausência de violações FK e 35 de 200 casos com publicações.
Foi corrigido o consolidador para processar extrações depois dos registros
DataJud e remapear `resultado.evidencias[].registro_id` pela mesma origem.
Referências ausentes, não inteiras ou de outro processo interrompem a união,
inclusive em dry-run. O JSON de relatório inclui `evidence_remappings` para
rastrear os IDs originais e de destino. A comparação lógica também normaliza
essas referências por identidade DataJud.

O teste da busca CJF recebeu `manifest=None`, reproduzindo o padrão do parser
CLI. A suíte completa após as correções passou: **134 testes**, incluindo
colisões de IDs, preservação das origens, deduplicação de extrações e rejeição
de evidências inválidas. `git diff --check` não indicou erros de whitespace.
Os bancos existentes não foram regravados: todas as origens auditadas tinham
zero extrações. A correção se aplica às próximas consolidações, inclusive à
importação futura da cópia remota que contém resultados da IA.

## Resumo executivo

Foi criado um SQLite novo a partir do SQLite local, pacote gzip de transferência e snapshot somente leitura do PostgreSQL ativo. Os registros foram unidos por identidades lógicas, IDs locais e chaves estrangeiras foram remapeados, e divergências DataJud foram preservadas em relatório. Duas uniões independentes produziram o mesmo conteúdo normalizado em 19 tabelas.

O piloto P1 consultou 200 casos selecionados de forma reproduzível. O Comunica retornou 35 casos com atos publicados; o CJF trouxe um acórdão, no mesmo conjunto de 35 casos, e o Arquivo TRF1 não encontrou documentos. A taxa de busca com resultado não mede procedência nem cobertura dos autos. Os indicadores INSS de P3 são agregados por UF/competência e não foram vinculados a processos ou pessoas.

## P0 — Auditoria e consolidação

### Origens e cópias de segurança

| Origem | Contagem auditada antes da união | Observação |
|---|---:|---|
| `data/bpc-remote.sqlite` | 12.224 processos; 12.283 hits DataJud; 105 versões documentais; 55 comunicações; 3 vínculos; 0 extrações IA | SQLite local, somente leitura |
| `transferencia/bpc-jud.sqlite.gz` | 2.584 processos; 2.588 hits DataJud; 42 comunicações; 0 extrações IA | gzip válido contendo SQLite |
| PostgreSQL ativo | 7.097 processos; 7.101 hits DataJud; 41 documentos; 42 comunicações; 0 vínculos documentais; 0 extrações IA | exportado para snapshot SQLite somente leitura |
| `transferencia/bpc-jud.dump` | dump custom PostgreSQL | inspecionado, não restaurado automaticamente |

Backups em `data/backups-luna-20261007-220831/`:

| Arquivo | SHA-256 |
|---|---|
| `bpc-remote.sqlite` | `27B0FAB78B1F7C9C8C9C37E417E90EBB6B843AAB39B8D144D52CDB80C1B673D0` |
| `bpc-jud.sqlite.gz` | `8202335B171AC556539B745EA2C40DB13BCDF4FB3EB3A9CD88A816FFFB834D0D` |
| `bpc-jud.dump` | `482CC7D5688F8DA5E71162557A7A89BE02C20F97CC8BCA95C1F8BFB779485D56` |
| `postgres-readonly-snapshot.sqlite` | `F428A55207492A397E5E28E9A32624D4197E808DF2CBCE23209FD7C79834CBF9` |

### Resultado da união

O arquivo consolidado foi criado com o schema SQLAlchemy da aplicação. Contagens após a união-base: 16.737 processos; 16.796 hits DataJud; 907.521 movimentos; 55 comunicações; 146 versões documentais; 3 vínculos documentais; 0 extrações IA. Após as coletas P1/P2: 110 comunicações, 168 versões documentais e 4 vínculos documentais; o universo de processos e hits DataJud não mudou, e seguem 0 extrações IA. A soma simples de bancos não foi usada: os conjuntos se sobrepõem. Códigos TPU, incluindo 6114/11946/11947, foram preservados como códigos de assunto, não tratados como IDs autoincrementais.

A união deduplicou 1.578 hits DataJud de forma idêntica entre fontes e reportou **2.020 comparações divergentes**, correspondentes a **1.010 identidades lógicas DataJud** divergentes em duas origens adicionais cada. O conteúdo não foi sobrescrito silenciosamente; consulte `data/conflitos-luna-final.json`, que registra cada origem e PK de origem/destino. Os mapas de identidade mantêm processos por CNJ, hits por índice+ID e as chaves contratuais de documentos, comunicações e extrações. Snapshots de indicadores não são somados.

Os três vínculos documentais originais pertencem a um mesmo caso do Piauí, fora do recorte. Na verificação final, 24 de 425 referências de arquivos de coletas estavam ausentes localmente; todas eram caminhos absolutos `/app/data/raw/...` provenientes do ambiente remoto. Nenhuma das 122 referências de Bronze de documentos públicos estava ausente. Esses arquivos remotos não foram apresentados como recuperáveis. O PostgreSQL ativo apresentava uma coleta DataJud em estado `executando`; não foi alterado nem forçado para estado terminal. O dump não foi restaurado, e a cópia remota mais recente de `extracoes_ia` não estava disponível: foram preservadas zero extrações entre todas as origens auditadas.

### Reprodutibilidade e validações

- Integridade SQLite: `integrity_check = ok`.
- Integridade referencial: zero violações de chaves estrangeiras.
- Duas novas uniões, em saídas separadas, foram comparadas por identidade e conteúdo normalizado: **19 tabelas coincidentes, zero divergências**.
- Testes direcionados: `pytest ingestion/tests/test_consolidation.py ingestion/tests/test_store_sqlite_backend.py -q` — **3 passaram**.
- Os testes cobrem colisão de IDs locais, chaves DataJud, nova versão documental, FKs remapeadas, extrações, snapshot de indicadores e recusa de saída existente.
- O coletor `PostgresStore` passou a usar operações de upsert compatíveis com SQLite sem mudar o comportamento PostgreSQL.
- Painel/API carregou processo com dados DataJud e comunicações (`0002051-98.2014.4.01.3501`) e processo com documento público ligado (`1024392-94.2020.4.01.3500`): ambos `GET /admin/api/processos/{CNJ}` responderam HTTP 200.

Comandos reproduzíveis e transferência constam em `README.md` e `scripts/consolidate_databases.py`. O arquivo novo não substitui `data/bpc-remote.sqlite`; mantenha os caminhos `data/raw/` referenciados na cópia usada pelo pesquisador.

## P1 — Documentos nos casos selecionados

### Desenho do piloto

O manifesto tem seed `20261007`, seleção estratificada por grupo territorial e ano, e inclui hierarquia de assunto 6114/11946/11947. A base de candidatos foi 3.823 CNJs: 1.793 do núcleo com código municipal DataJud 743 (DF), 1.031 Formosa (1798) e 999 Luziânia (2788). A amostra de 200 contém 100 do núcleo DF, 50 de Formosa e 50 de Luziânia; os 50 casos iniciais são subconjunto dos 200. Os manifestos preservam o motivo de inclusão e os atributos de seleção.

Os códigos representam o município do órgão julgador no payload DataJud, não residência da parte. Formosa e Luziânia são candidatos territoriais suplementares; associação à sede não prova domicílio. TRF6/Unaí e tribunais estaduais continuam fora da coorte principal.

### Cobertura por fonte

| Fonte | CNJs consultados | Com resultado | Erro/bloqueio | Observação |
|---|---:|---:|---:|---|
| CJF/JEF1 | 200 CNJs distintos; 204 tentativas (4 repetições) | 1 caso com acórdão CNJ exato | 0 falha/bloqueio; 199 sem resultado únicos | busca explícita por manifesto |
| Arquivo TRF1 | 200 | 0 | 0 falha/bloqueio; 200 sem resultado | consultas CNJ individuais; sem resultado não significa autos ausentes |
| Comunica PJe | 200 | 35 casos com comunicação; 56 comunicações | 0 erro final; 165 sem resultado; 29 respostas HTTP 500 transitórias foram repetidas até HTTP 200 | publicações/atos, não inteiro teor dos autos |

No conjunto de 200, 35/200 casos tiveram algum item público em pelo menos uma fonte; o acórdão CJF está entre os mesmos 35 casos encontrados no Comunica. Treze casos (13/200) têm peça classificada como sentença, decisão ou acórdão no Comunica: 9/200 com `Sentença Tipo C`, 2/200 com `Decisão` (um caso é incidental) e 3/200 com `Acórdão`, com sobreposição de tipos. Um caso com ato incidental classificado como `Decisão` trata de habilitação sucessória/RPV durante cumprimento de sentença, não do mérito inicial. Em revisão manual de até 10 documentos positivos, 4/200 casos forneceram desfecho processual verificável: três sentenças encerram mandados de segurança sem resolução de mérito e um acórdão informa o resultado de recurso. Motivo administrativo explícito do indeferimento: 0/200. Não há base para chamar esses valores de taxa de procedência.

| Grupo do manifesto | CNJs | Casos com comunicação | Peça formal (sentença/decisão/acórdão) |
|---|---:|---:|---:|
| Núcleo TRF1/DF (código DataJud 743) | 100 | 18 | 5 |
| Formosa | 50 | 7 | 5 |
| Luziânia | 50 | 10 | 3 |

Os resultados se concentram em casos mais recentes: 12/14 selecionados de 2026 tiveram comunicação, contra 7/16 de 2025 e 4/11 de 2024. Entre 2018–2023, foram 3/123 (2/23 em 2019 e 1/22 em 2020; nenhum em 2018, 2021, 2022 ou 2023). A diferença por ano é compatível com menor cobertura temporal de publicações, e não deve ser interpretada como diferença de mérito.

Os documentos revistos foram classificados pelo tipo e pelo teor do dispositivo; sentenças Tipo C sobre mandados de segurança indicam extinção processual sem julgamento do pedido de BPC. O acórdão CJF é uma publicação/ementa curta, confirma o CNJ exato e informa resultado recursal, sem motivo administrativo explícito. O ato incidental do Comunica foi revisto e excluído da categoria “decisão de mérito”. Não foram enviados textos a serviço externo. O registro de revisão local está em `data/revisao_piloto_luna.md`.

### Diários históricos TRF1

O portal oficial expõe cadernos por seção e data. Foi preservado o PDF de Goiás de 14/02/2022 em `data/raw/edjf1/2022-02-14/`, com hash SHA-256 `460003637dc437741c502be79440f1965f3ac778831a7ff9b374fa78cc80a652`. A edição contém apenas a indicação “Não há atos judiciais a serem divulgados nesta data”; não foi associado processo algum a partir dela. O portal também mantém arquivo eletrônico com publicações em DOC/TIFF; esses são atos já publicados, não autos completos.

## P2 — Corpus complementar e fontes institucionais

Foram consultadas 5 URLs em cada fonte TNU, TRF2, TRF4, TRF5 e TRF6 — 25 URLs no total, dentro do limite de 100. As consultas utilizaram “benefício de prestação continuada”/“benefício assistencial”. Foram obtidas 8 versões TNU, 4 TRF2, 2 TRF4, 5 TRF5 e 2 TRF6 (21 no total). São julgados selecionados por pesquisa textual, não amostra representativa e sem vínculos automáticos com casos do piloto.

STJ: havia uma execução anterior interrompida após gravar um documento e marcar a coleta como falha no próximo recurso. Para diagnóstico, o mesmo recurso oficial JSON da Segunda Turma foi comparado com `curl` e `urllib`: ambos responderam a uma faixa de 1.024 bytes em menos de 1,1 s (HTTP 206); a leitura completa de 1.410.751 bytes pelo Python retornou HTTP 200 em 0,369 s e 338 registros JSON. Uma reexecução limitada a um recurso/um documento concluiu; não criou versão nova porque o documento já existia. A demora anterior não foi reproduzida e não se tentou um lote grande. TRF3 permanece indisponível por timeout tanto na pesquisa pública quanto na consulta direta já registrada. TJMG exige CAPTCHA na busca jurisprudencial automatizada; essa fonte foi interrompida sem contorno. Não foram fabricados IDs ou tentadas rotas privadas.

IpeaJus: referências acadêmicas de 2018 descrevem uso histórico de microdados, diários e sentenças, mas a busca não encontrou API, catálogo de microdados ou código público vigente para integração. Foi preparado um rascunho de pedido de informação/acesso em `docs/RASCUNHOS_SOLICITACAO_ACESSO.md`; nenhum pedido foi enviado ou protocolado.

## P3 — Contexto administrativo agregado

Selecionaram-se junho, julho e agosto de 2026, as três competências mensais consecutivas mais recentes listadas no catálogo consultado. Para cada competência, foram baixados uma vez os recursos de indeferimentos e concessões e reutilizados para DF, GO e MG. Os seis arquivos-fonte foram preservados em `data/raw/inss_staging_luna/`; cópias comprimidas ligadas às coletas também estão na Bronze. SHA-256 dos XLSX:

| Competência | Indeferimentos | Concessões |
|---|---|---|
| 202606 | `c28015316349195a121b68925d43776567e88b4cf0bd3e775852c623bad42fee` | `7ec6e6f28caa64cde2b1b8bef29dcc45ba63093ceb5a6fc1a42c07b2f5001579` |
| 202607 | `c1ab55e72db6885f824cdd99a7906c65870a976104f2cfa4177e8969ffc86c12` | `1584d260d2268399f9d883ed1cce3ce1c7e3759d60b167c5c4383d4439d66581` |
| 202608 | `2420b50739061727217995173e0a3e8982e0bc06f9568f293754e04bb8c250c8` | `cadfbcdffbf7e765cf05ba76be8d31c2b09d3f39d525bd6f19edda561e1ef5d1` |

Quantidade agregada por UF/competência, como reportada pelo importador (eventos de concessão/indeferimento, não pessoas únicas):

| Competência | Indeferimentos DF | GO | MG | Concessões DF | GO | MG |
|---|---:|---:|---:|---:|---:|---:|
| 202606 | 3.759 | 6.841 | 16.923 | 1.714 | 2.317 | 10.019 |
| 202607 | 5.662 | 7.050 | 16.477 | 2.542 | 3.013 | 11.586 |
| 202608 | 3.647 | 7.546 | 14.812 | 2.162 | 2.871 | 10.825 |

Em agosto/2026, DF já existia na base com os mesmos hashes e quantidades: o agregador inseriu zero linhas novas para as duas tabelas, sem duplicar snapshots.

Esses números são totais agregados por UF, espécie e motivo/despacho. Não identificam município da RIDE nem podem ser associados a pessoa ou processo por coincidência de local ou data. Não são taxa de concessão judicial.

### Referências Bronze remotas ausentes

As 24 referências abaixo apontam para `/app/data/raw` no host remoto e não existiam nesta cópia local:

```text
/app/data/raw/comunica_pje/processos/2026-08-27/1744b720-c675-468e-bc18-eb93c1b072c7.ndjson.gz
/app/data/raw/comunica_pje/processos/2026-08-27/7f007ee1-a57b-479a-893d-2b3a1aa63a69.ndjson.gz
/app/data/raw/comunica_pje/processos/2026-08-27/9e9b6996-ba5e-4887-a362-dd623e5f4fc5.ndjson.gz
/app/data/raw/comunica_pje/processos/2026-08-27/c3877a15-8dcc-434d-a0d0-b9fa3c9d8ee1.ndjson.gz
/app/data/raw/comunica_pje/processos/2026-09-22/03b0d327-94ce-4de6-8b61-3666e310ff0a.ndjson.gz
/app/data/raw/comunica_pje/processos/2026-09-22/c4adb825-bdfd-433c-8f94-c4123b603047.ndjson.gz
/app/data/raw/datajud/stj/2026-09-01/d7b9ad3b-b399-4a36-b1ba-69bd81f27e55.ndjson.gz
/app/data/raw/datajud/trf1/2026-08-27/0976fb36-5904-4311-8f61-e25de12a1ee8.ndjson.gz
/app/data/raw/datajud/trf1/2026-08-27/574ca012-80c5-401a-be8b-c178a1489125.ndjson.gz
/app/data/raw/datajud/trf1/2026-08-27/7c90ccd2-2561-4022-bad7-c50537a79f9f.ndjson.gz
/app/data/raw/datajud/trf1/2026-08-27/bcc51a82-84a7-47d8-b807-d040f1fb5440.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/0af07888-74af-4b51-aa01-5c23e8d63d5e.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/15f46eb8-6fbe-420d-b126-033ca54e53f5.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/41319de5-67c3-4ae6-8898-a76037db42c7.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/579e9559-2d9b-498e-aa46-50ac0d0cac43.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/5f260c5e-e1d9-4c5e-b382-abf37c2af111.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/7023c849-3301-45f5-84ef-5c2c58a5685d.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/77b5151e-e488-4040-812d-1a8e5a3affd3.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/c15877dc-42ab-4649-815e-66ba5a6cc7a3.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/c60614c7-2bb3-4501-91e8-3997e5386f1c.ndjson.gz
/app/data/raw/datajud/trf1/2026-09-22/d300637c-b5e2-4d4c-b044-bed6d92d752b.ndjson.gz
/app/data/raw/transparencia_bpc/municipios/2026-09-22/42162e81-391c-4d5f-b42f-9c7412b5764f.ndjson.gz
/app/data/raw/transparencia_bpc/municipios/2026-09-22/b45dd722-3b42-426e-a60b-ef7b38c4c830.ndjson.gz
/app/data/raw/transparencia_bpc/municipios/2026-09-22/fd204e05-8d65-4213-8667-e64485470a19.ndjson.gz
```

## Pendências e limites

- A extração atual do PostgreSQL não continha resultados `extracoes_ia`; verificar/importar uma cópia mais recente se o pesquisador precisar desses resultados.
- O dump PostgreSQL de transferência não foi restaurado; a consolidação usa snapshot do banco ativo.
- Publicações são cobertura documental parcial, distinta de autos completos. Ausência nas consultas não demonstra inexistência de peça processual.
- Motivo administrativo explícito, perfil pessoal e resultado de mérito permanecem ausentes quando o documento não os afirma.
- A base consolidada é cópia local para revisão, não foi promovida à instância remota nem exportada para Git.
- Permanecem três saídas intermediárias de consolidação marcadas como inválidas/superadas: `data/bpc-consolidado-20261007-231500.sqlite`, `data/bpc-consolidado-repro-20261007.sqlite` e `data/conflitos-luna-repro.json`. A tentativa de removê-las foi rejeitada pela política de ferramenta; não usar esses arquivos. A base correta é `data/bpc-consolidado-luna-20261007.sqlite`.
