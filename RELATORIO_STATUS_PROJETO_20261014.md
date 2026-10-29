# Relatório de evolução do projeto BPC Jud

**Atualizado em:** 15/10/2026, 19:14  
**Banco conferido:** `data/bpc-consolidado-luna-20261007.sqlite`

## Em uma frase

Saímos de uma coleta concentrada em metadados do DataJud e poucas comunicações/documentos para uma base com **16.737 processos**, **39.515 documentos e versões públicas** e dados administrativos e sociais de contexto. Isso amplia a amostragem e a comparação jurídica; ainda não significa que temos o inteiro teor dos 16.737 casos, nem que já sabemos por que cada pessoa entrou na Justiça.

## O que mudou

| Área | Antes da ampliação | Situação conferida agora | O que isso permite |
|---|---|---|---|
| Processos | Coleta centrada nos metadados e movimentações do DataJud. | 16.737 processos únicos, 16.796 registros DataJud e 907.521 movimentações. | Encontrar e acompanhar casos dos assuntos selecionados, com mais escala. Movimentações não substituem as decisões em texto. |
| Publicações e documentos | Cerca de 146 documentos/versões no início da ampliação. | 39.515 documentos/versões públicos; 830 vínculos documentais confirmados com processos. | Pesquisar e comparar decisões, e consultar texto do próprio processo quando houver documento vinculado. O total inclui versões, não processos únicos. |
| PJe e comunicações | 55 comunicações na cópia inicial. | 1.241 consultas PJe e 302 comunicações registradas; há também documentos públicos consultados no PJe/TRF1. | Procurar publicações e documentos associados a um número CNJ. Não equivale a acesso completo aos autos. |
| Contexto administrativo/social | Fontes ainda em levantamento. | Dados agregados de INSS, CGU/Portal da Transparência, MDS/SUAS e IBGE organizados no projeto. | Situar os casos em tendências territoriais e administrativas, sem atribuir estatísticas agregadas a uma pessoa. |
| IA | Sem resultado integrado à cópia consolidada do banco. | Piloto IpeaIA e formato de triagem preparados; **0 extrações salvas neste banco**. Houve testes no ambiente remoto. | Próximo passo é importar/testar resultados, guardar explicações legíveis e evidências, revisar uma amostra e só então ampliar. |

## Fontes: o que temos e como cada uma ajuda

### 1. Encontrar e acompanhar os processos estudados

| Fonte | Dados disponíveis | Papel na pesquisa | Limite importante |
|---|---|---|---|
| **DataJud/CNJ** | Número CNJ, tribunal, grau, classe, órgão julgador, assuntos e movimentos. A coleta foi orientada pelos assuntos 6114, 11946 e 11947. | É a base da amostra: identifica processos e descreve sua tramitação. | Não fornece, por si só, petição inicial, fundamentação ou inteiro teor da decisão. |
| **TPU/CNJ** | Vocabulário padronizado de assuntos, classes e movimentos. | Ajuda a interpretar os códigos do DataJud de forma consistente. | É referência de classificação, não uma nova coleção de casos ou documentos. |
| **Comunica PJe / DJEN** | Consultas por número CNJ e comunicações/publicações localizadas. | Pode indicar atos publicados e apontar para documentos relacionados. | Uma comunicação pode conter só dados de intimação; não é API de inteiro teor. |
| **PJe público do TRF1** | Documentos e páginas públicas em HTML quando disponíveis. | Pode trazer texto do próprio processo da amostra, sendo uma das fontes mais valiosas para entender o caso individual. | Cobertura parcial. O vínculo só deve ser aceito quando o número/identidade do processo for confirmado. |

### 2. Jurisprudência pública para comparação

São **39.515 documentos/versões**, não 39.515 processos novos. Esses julgados ajudam a identificar teses, vocabulário e padrões em casos semelhantes; não provam o que aconteceu nos processos individuais da amostra DF/RIDE.

| Origem | Documentos/versões | Como ajuda |
|---|---:|---|
| **CJF/TRF1 — JEF1** | 18.535 | Corpus amplo de decisões federais e de Juizados para comparar argumentos e entendimentos assistenciais. |
| **TRF6** | 9.310 | Acrescenta julgados federais e recursais para comparação regional; a retomada pública voltou a render. |
| **TRF4** | 5.470 | Decisões de TRU e Turmas Recursais; buscas por BPC seguem rendendo. |
| **TRF2** | 3.048 | Decisões federais sobre benefício assistencial; coleta pública ainda produtiva. |
| **TRF5** | 1.351 | Mais material comparativo; expansão esbarrou em formatos de página não reconhecidos. |
| **TNU** | 766 | Entendimentos que uniformizam questões dos Juizados Especiais Federais. |
| **STJ** | 425 | Contexto de tribunal superior e comparação de teses. |
| **PJe público TRF1** | 603 | Documentos encontrados em páginas públicas do tribunal; alguns podem corresponder aos próprios processos da amostra. |
| **Arquivo TRF1** | 7 | Documentos públicos localizados pontualmente. |

### 3. Contexto administrativo e social

| Fonte | Conteúdo reunido | Como ajuda | O que não permite concluir |
|---|---|---|---|
| **INSS — indeferimentos e concessões** | 467 agregados de indeferimentos e 185 de concessões. | Comparar tendências por período, UF, espécie e despacho; concessões atualizadas até 2026-09. | Não revela o motivo administrativo de um processo individual. |
| **CGU / Portal da Transparência** | 124 indicadores de valores e estoques de BPC por município e tipo. | Descrever distribuição territorial e cobertura. | Valor/município agregado não prova residência nem resultado judicial de uma parte. |
| **MDS — Censo SUAS** | 8.557 registros sobre equipamentos e serviços socioassistenciais. | Contextualizar a oferta local de serviços. | Não identifica usuários individuais. |
| **IBGE/SIDRA e MDS/VIS DATA** | Séries e arquivos agregados demográficos, sociais e de BPC. | Contextualizar território e tendências. | Não devem ser associados individualmente aos litigantes. |
| **CRPS — consulta manual** | Quatro protocolos consultados pelo pesquisador. | Ementas, votos e decisões podem ajudar a estudar a etapa administrativa anterior à ação judicial. | Ainda não há coleta automatizada; depende de consulta assistida pelo pesquisador. |

## Como as fontes se complementam em um caso

1. **DataJud** identifica o processo e fornece a linha do tempo.
2. **Comunica PJe/DJEN** procura comunicações e publicações associadas ao número CNJ.
3. **PJe público/TRF1** pode fornecer documentos do próprio caso, se estiverem acessíveis e o vínculo for confirmado.
4. **CJF, TRFs, TNU e STJ** ajudam a comparar a decisão com jurisprudência; não substituem documentos do caso estudado.
5. **INSS, CGU, MDS e IBGE** oferecem contexto agregado, não evidência individual.
6. **IpeaIA** deve resumir e classificar apenas o que as fontes efetivamente mostram, citando evidências e declarando lacunas.

## Tratamento com IA: estado e avanço esperado

O piloto foi desenhado para produzir, por processo, uma explicação em linguagem natural acompanhada de campos estruturados: escopo provável do pedido, aderência geográfica, nível de evidência, evidências citadas, lacunas e necessidade de revisão humana. Também deve preservar modelo, versão do prompt e resposta original.

**Estado atual:** houve testes da chamada à IpeaIA no ambiente remoto, mas esta cópia consolidada do banco registra **zero extrações**. Portanto, ainda não há resultados da IA disponíveis aqui para consulta no banco/painel.

**O que queremos alcançar:** guardar a análise como texto legível junto com classificação, fontes usadas, trechos/evidências e lacunas; permitir abrir cada processo e conferir os dados originais e a análise; revisar manualmente um lote-piloto e medir erros antes de processar a amostra toda. A IA só deve atribuir motivo da judicialização, fundamentos ou resultado quando houver evidência documental do próprio processo. Sem isso, deve marcar como indeterminado — nunca preencher a falta usando um caso parecido de outro tribunal.

## Próximos avanços esperados

### Mais e melhores fontes

- Continuar as consultas públicas produtivas: **TRF2 — benefício assistencial, próxima página 537; TRF4 — BPC, próxima página 581; TRF6 — BPC/Turmas Recursais, próxima página 451**. Em relação ao snapshot de 14/10, as fontes acrescentaram 449 versões no TRF2, 1.006 no TRF4 e 99 no TRF6; páginas com itens inválidos foram puladas, preservando os documentos anteriores.
- No TRF4, retomar as alternativas em **LOAS, página 20; benefício assistencial, página 18; amparo social, página 13**. Nesta rodada, LOAS não trouxe itens novos; benefício assistencial acrescentou 11 e amparo social 8.
- TRF5 e TNU responderam sem autenticação, mas os primeiros 50 resultados de cada consulta testada já estavam concluídos/deduplicados, sem novos documentos. O teste de TRF2 na página 526 encontrou card sem links únicos e foi retomado na página 527; no TRF4, o documento `711775766662818015642763916019` falhou no layout na página 555; no TRF6, o documento `381770920126128211065497442305` falhou na página 450. Não repetir esses itens; retomar nas páginas seguintes.
- INSS concessões: setembro/2026 validado e importado (19 agregados novos). O recurso de indeferimentos rotulado como setembro/2026 tinha competência interna 202605, portanto foi rejeitado e preservado apenas como Bronze; outubro/2026 ainda não tinha recurso de concessões no catálogo. Censo SUAS 2025 já está armazenado (8.557 agregados); não houve alteração.
- Priorizar o aumento de documentos **dos próprios processos DF/RIDE**, não apenas o crescimento do corpus de jurisprudência. Medir quantos documentos estão ligados com segurança à amostra e quantos contêm texto útil de inicial, decisão ou sentença.
- TRF6 voltou a responder e segue em coleta; no TRF5, as primeiras páginas BPC/benefício assistencial foram consultadas sem autenticação, mas só continham links já coletados. O acesso direto a documentos do TRF3 continua sendo a barreira; não contornar controles nem repetir tentativas sem mudança de disponibilidade.
- Retomar a consulta assistida do **CRPS** quando o pesquisador puder fornecer os textos dos protocolos; manter esse material separado dos autos judiciais.
- Avaliar o **MCP Jurídico Brasil** como ferramenta de descoberta/acesso depois de verificar origem, cobertura, permissões e formato. MCP é um meio de acesso, não uma fonte em si.

### IA e consulta no painel

- Importar os resultados feitos no ambiente remoto para o banco consolidado, preservando processo, modelo e versão do prompt.
- Rodar um lote pequeno e revisar manualmente as respostas antes de escalar.
- Exibir por processo metadados, movimentações, documentos vinculados e explicação da IA, com evidências e lacunas visíveis.
- Medir cobertura documental, proporção de campos indeterminados e concordância com revisão humana.
- Manter separadas as conclusões apoiadas por documentos do caso e as comparações com jurisprudência externa.

## Retrato da cópia do banco conferida

| Indicador | Quantidade |
|---|---:|
| Processos únicos | 16.737 |
| Registros DataJud | 16.796 |
| Movimentações | 907.521 |
| Consultas PJe | 1.241 |
| Comunicações PJe | 302 |
| Documentos/versões públicos | 39.515 |
| Vínculos de documentos com processos | 830 |
| Extrações IpeaIA salvas nesta cópia | 0 |

**Integridade conferida:** `PRAGMA quick_check = ok`; nenhuma violação de chave estrangeira.  
**Banco:** `data/bpc-consolidado-luna-20261007.sqlite`.

**Snapshot validado:** `data/backup-coleta-fontes-publicas-20261015-1913.sqlite`, 1.445.421.056 bytes, SHA-256 `93ADD99128D59EA90BDE480DE22AC18B2B3FC7202B100B92CA8089B075CC1BA8`. O próprio arquivo contém 39.515 documentos/versões; `quick_check=ok` e nenhuma violação de chave estrangeira.

## Mensagem curta para a reunião

“Ampliamos a coleta de cerca de 146 para 39.515 documentos e versões públicas, mantivemos 16.737 processos identificados pelo DataJud, incorporamos consultas/comunicações do PJe e dados agregados do INSS, CGU, MDS e IBGE. As novas fontes aumentam a comparação jurídica e o contexto social. A principal lacuna é obter documentos dos próprios processos da amostra. O piloto de IA já foi testado, mas seus resultados ainda não foram importados para o banco consolidado. O próximo passo é ampliar documentos vinculados aos casos, integrar e revisar as análises da IA e disponibilizá-las por processo no painel.”

## Materiais de apoio

- `docs/CONTRATOS.md` — schemas e decisões sobre os dados.
- `docs/ESCOPO_PESQUISA.md` — recorte DF/RIDE e desenho metodológico.
- `docs/FONTES_ABERTAS.md` — histórico detalhado das coletas, limites e retomadas por fonte.
- `PENDENCIA_AUTOMACAO_CRPS.md` — pendências para coleta assistida no CRPS.
- `RELATORIO_EXECUCAO_COLETA_LUNA.md` — histórico de consolidação e validações.
- `RESTAURAR_BANCO.md` e `SEM_DOCKER.md` — transferência/restauração e execução sem Docker.
