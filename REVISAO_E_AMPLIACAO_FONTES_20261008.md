# Revisão e ampliação das fontes públicas — 08/10/2026

## Escopo da rodada

Ampliar os cinco coletores já viáveis (TNU/TRF2/TRF4/TRF5/TRF6), completar
janeiro–agosto/2026 de indeferimentos e concessões INSS para DF/GO/MG e
inventariar o corpus textual inteiro. CRPS é pendência separada de login
assistido; não foi consultado automaticamente.

Banco explícito: `data/bpc-consolidado-luna-20261007.sqlite`. Base inicial
desta rodada: **232 versões documentais**, 220 comunicações,
16.737 processos, seis vínculos documentais e zero extrações IA.

## Jurisprudência

Busca `LOAS`, até 20 páginas e 50 URLs novas por fonte, timeout 25 segundos.
TRFs: origem do próprio tribunal; sem consulta automática de autos. Fontes
públicas, sem credenciais ou contorno de CAPTCHA. Não é coleta exaustiva.

| Fonte | URLs concluídas novas | Versões novas | Corpus final |
| --- | ---: | ---: | ---: |
| TNU | 50 | 109 | 166 |
| TRF2 | 50 | 47 | 81 |
| TRF4 | 50 | 50 | 82 |
| TRF5 | 50 | 49 | 80 |
| TRF6 | 50 | 48 | 85 |

Ganho: **303 versões**, total **535** documentos. URL sem documento temático
é registrada como tal; não criar documento artificial. TNU agrupa múltiplos
artigos numa URL, explicando mais documentos que URLs.

A primeira busca TNU falhou após 30 URLs concluídas, preservando seus 60
documentos. Cabeçalho real de Reclamação incluía o CNJ principal e um segundo
CNJ explicitamente rotulado `PROCESSO ORIGINÁRIO`. O parser agora exige um
único principal no segmento anterior ao rótulo; números ambíguos sem rótulo
continuam rejeitados. Contrato atualizado antes da correção; regressões testam
não vincular o originário. A retomada pulou os sucessos e concluiu mais 20 URLs
com 49 documentos. A coleta falha antiga permanece para auditoria.

Vínculos: seis → oito, ambos novos TRF6 a processos já existentes:
`1023289-86.2019.4.01.9999` e `1020386-78.2019.4.01.9999`.
Identidade explícita não confirma DF/RIDE, residência ou concessão inicial.
Nenhum processo novo, nenhuma inferência por nome/similaridade.

## Auditoria integral de disponibilidade

Comando reproduzível (saída deve ter nome novo):

```powershell
$env:PYTHONPATH = 'ingestion/src'
.\.venv\Scripts\python.exe -m bpc_ingestion.corpus_audit --database data/bpc-consolidado-luna-20261007.sqlite --output data/auditoria-corpus-20261008-ampliado-v1.json
```

Artefato local produzido: `data/auditoria-corpus-20261008-ampliado-v1.json`.
Examinaram-se **755 itens**: 535 documentos + 220 comunicações. Sem escrita
no banco e sem serviço externo; campos, hashes e posições permitem voltar à
fonte. Não exporta contexto pessoal nem trechos de casos para o relatório.

- 730 itens têm campo `texto`: 510 documentos e 220 comunicações.
- 22 documentos STJ têm espelho/ementa, não campo `texto` de inteiro teor.
- Três versões do arquivo TRF1 permanecem sem texto extraído.
- 734 textos principais distintos; 17 grupos de texto exatamente igual,
  com 18 itens excedentes. Versões não foram apagadas.
- 26 itens têm texto disponível com menos de 600 caracteres; tamanho não
  prova irrelevância, mas orienta revisão.
- Oito comunicações antigas contêm possível HTML residual; preservadas com
  alerta, não reescritas silenciosamente.

Pistas nos 535 documentos: renda 269; deficiência 350; idade 246; cadastro 67;
cessação/restabelecimento 151; demora 34; linguagem dispositiva 106; expressão
literal de indeferimento administrativo 44. São ocorrências sobrepostas em
versões documentais, não motivos confirmados, prevalências ou pessoas únicas.
Nas 220 comunicações, a mesma regra encontrou 15 itens com pista de demora
e zero com as duas expressões literais de negativa administrativa pesquisadas.
Ausência da expressão não comprova ausência do motivo.

## Revisão qualitativa dirigida — cinco documentos

Seleção não aleatória: para cada uma das cinco fontes, o documento de maior
ID com expressão literal de negativa; na ausência, maior ID da fonte.
Leitura dirigida dos segmentos relevantes, não revisão semântica integral de
todos os 535 textos. Resultados abaixo são observações de conteúdo para orientar
revisão, não extrações validadas de desfecho/negativa.

| ID local / fonte | Observação | Cuidado necessário |
| --- | --- | --- |
| 469 / TNU | Discussão sobre impedimento de longo prazo e atividade remunerada, com votos divergentes. | A expressão negativa administrativa aparece em precedente sobre benefício por incapacidade; não atribuí-la ao motivo de negativa de BPC do caso. |
| 420 / TRF2 | Discussão de requisito de deficiência, critério socioeconômico e implantação de BPC em tutela recursal. | Distinguir alegações, fundamentação do juízo e concessão provisória; não registrar como sentença final procedente. |
| 440 / TRF4 | Discussão de admissibilidade de recurso especial, com precedentes previdenciários/assistenciais. | Referências a negativa e prazo em precedentes não comprovam motivo individual; inadmissão recursal não é resultado do pedido inicial. |
| 535 / TRF5 | Ementa registra mudança do pedido de outro benefício para LOAS durante a instrução e controvérsia sobre início do pagamento. | Reforma da data de início não equivale a negar integralmente o BPC. |
| 335 / TRF6 | Dispositivo discute abatimento de BPC nos atrasados de pensão. | Tema principal é pensão; candidato lexical não deve entrar automaticamente em amostra de concessões iniciais BPC. |

Hashes das versões lidas, para reencontrar a evidência local:

- 469: `d7e6c97d9bebf95ea48ec2c6e70f1e39525013e621df2697791e39aa96ce43cd`
- 420: `08782cd1493fa97a36568675d7092ac9c2e4a0d9f6d677c6d8200e5c8744c046`
- 440: `4fec9c89b4a2937c65cc77f05c8941628314b6cc8b99aee33876cbd37a961e80`
- 535: `592a160a0a2b2cbf2e9ee341e83b82ceea6cbe19422ea11ca7bef1dee7fce5b0`
- 335: `bcbe05f90aad9227751fcc22e401922dc4c459b35b5e0f2b0e756d2be52b55c2`

## INSS e verificações finais

Cobertura janeiro–agosto/2026 completa para DF/GO/MG em ambas as tabelas.
Cada par competência/UF possui um snapshot de arquivo, sem soma de versões.
Novas importações: janeiro–abril de indeferimentos e janeiro–maio de concessões.
`--ufs DF GO MG` permite leitura única por mês, mantendo `--uf DF` compatível.
Contagens multi-UF foram comparadas com união de filtros individuais em testes;
competência incorreta, inclusive em linha de outra UF/espécie, rejeita a importação.

| Competência | Indeferimentos BPC | Concessões BPC |
| --- | ---: | ---: |
| 202601 | 8.310 | 3.752 |
| 202602 | 22.089 | 16.549 |
| 202603 | 32.979 | 14.696 |
| 202604 | 21.626 | 9.420 |
| 202605 | 26.401 | 9.859 |
| 202606 | 27.523 | 14.050 |
| 202607 | 29.189 | 17.141 |
| 202608 | 26.005 | 15.858 |

Total contextual do período nas três UFs: 194.122 indeferimentos (467 grupos)
e 101.325 concessões (166 grupos). Ganho desta rodada: 85.004 indeferimentos
em 211 grupos e 54.276 concessões em 98 grupos. Contagens são registros
administrativos das planilhas, não pessoas únicas, casos judiciais ou uma coorte
comum; não calcular taxa de sucesso dividindo essas colunas. Despacho não é
rotulado como concessão judicial sem dicionário e validação.

Microdados continuam só na Bronze local; persistência Silver restrita a agregados
administrativos, sem vínculo CNJ. Nenhum documento/registro enviado à IpeaIA.
O pacote antigo de transferência não foi atualizado e não acompanha estes ganhos.

Suíte completa: **165 testes passaram**, dois avisos de depreciação já existentes.
Auditoria lexical não é revisão humana/semântica validada e não escreveu extrações IA.

Verificação final no banco: `integrity_check = ok`, zero violações de chave
estrangeira; 16.737 processos, 16.796 registros DataJud, 907.521 movimentos,
220 comunicações, 851 consultas e zero extrações IA preservados.
As 48 combinações fonte administrativa/competência/UF esperadas foram conferidas
diretamente: 24 por tabela, um snapshot de arquivo por combinação.
Nenhuma coleta desta rodada permanece `executando`; a falha TNU anterior à
correção permanece documentada, não convertida em sucesso.

Todos os 319 arquivos gzip das pastas das 266 coletas desta rodada passaram
leitura/CRC; as 266 referências Bronze do banco existem e são legíveis. SHA-256
dos arquivos INSS foi conferido contra a Silver. O inventário contém exatamente
os IDs das duas tabelas textuais; todos os hashes textuais e intervalos de
ocorrência foram conferidos contra o texto atualmente armazenado.

SHA-256 da auditoria local:
`eb6b8540efeddce87678ebaada6900a72da03ae7544b2270b324128e4edefe19`.
Não houve commit/push, restauração de banco ou alteração do submódulo.

## Pendências externas e limite da conclusão

Comunica: nova sondagem única após a coleta ainda respondeu HTTP 503; lote não
retomado, nenhuma falha tratada como vazio e nenhuma retentativa em massa.
CRPS: automação assistida anotada separadamente, aguarda acesso do pesquisador.
Esta rodada não esgota os portais nem resolve disponibilidade dos autos DF/RIDE.
Fonte de conteúdo individual continua sendo publicação explicitamente vinculada;
sem texto do próprio caso, motivo/desfecho permanecem indeterminados. Jurisprudência
de outras regiões e INSS qualificam contexto/categorias, não preenchem essa lacuna.
