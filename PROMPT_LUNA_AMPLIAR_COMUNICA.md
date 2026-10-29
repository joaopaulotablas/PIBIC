# Luna — retomar e ampliar conteúdo publicado dos casos BPC

Você deve executar a coleta, não apenas propor um plano. Leia primeiro
`docs/CONTRATOS.md` integralmente e respeite seus schemas, identidades e limites.
Leia também `RELATORIO_EXECUCAO_COLETA_LUNA.md` e `docs/ESCOPO_PESQUISA.md`.

## Objetivo

Enriquecer processos existentes dos assuntos 6114, 11946 e 11947 com publicações
do Comunica, especialmente textos rotulados sentença, decisão e acórdão.
Não criar processos novos, não tratar publicação como autos completos e não
inferir motivo administrativo ou procedência somente pelo tipo do documento.

## Estado do trabalho em 08/10/2026

- Banco de trabalho: `data/bpc-consolidado-luna-20261007.sqlite`.
- Não usar implicitamente o PostgreSQL do `.env` nem `data/bpc-remote.sqlite`.
  Defina `DATABASE_URL` explicitamente para o SQLite acima em cada execução.
- Antes deste lote: 16.737 processos, 168 versões em `documentos_publicos`,
  quatro vínculos documentais e 110 comunicações.
- Backup anterior: `data/backup-pre-comunica-20261008.sqlite`.
- Manifesto atual: `data/manifesto-comunica-200-20261008.csv`.
  São 200 CNJs antes sem linha em `consultas_pje`: 100 núcleo Brasília,
  50 Formosa e 50 Luziânia. Os grupos refletem órgão julgador, não residência.
- A seleção usou semente 20261008 e rodízio por ano/combinação de assuntos,
  após excluir consultados de um manifesto candidato de 2.000 casos criado
  por `scripts/create_pilot_manifest.py`. Não é amostra aleatória simples nem
  amostra representativa de todos os 3.823 candidatos do recorte.
- A execução foi interrompida por pedido do pesquisador para passar a você.
  Na última leitura: 136 consultados (30 encontrados, 106 sem resultado),
  64 pendentes e 151 comunicações no banco, aumento de 41.
  **Reconte antes de executar: estas são contagens de passagem.**
- ID da coleta interrompida: `8ed0515fabfb45b89671e6768f730c02`.
  Verifique status e Bronze; não a marque concluída por ter resultados parciais.
  Foi marcada `falhou` para encerrar o status executando após a interrupção;
  isso não significa falha da API. Foram registrados 41 itens novos.
  Uma interrupção abrupta pode deixar gzip incompleto. Preserve o arquivo;
  valide sua leitura e registre eventual indisponibilidade, sem inventar Bronze.

## Execução

1. Confira que não existe outro coletor escrevendo no banco. Faça novo backup
   SQLite consistente usando API de backup; não sobrescreva backups existentes.
2. Confira integridade, FKs e contagens. Preserve alterações do worktree, inclusive
   submódulo `jeferson/bpc-loas`. Não faça reset, commit ou push.
3. Leia o manifesto e compare cada CNJ com `consultas_pje` e `processos`.
   Consulte somente pendentes; não repita `encontrado`/`sem_resultado`.
   Registre erros separadamente e retente apenas falhas temporárias, de forma limitada.
4. Reutilize `ComunicaPjeClient`, `collect_comunica`, `BronzeWriter` e
   `PostgresStore` com o SQLite explicitamente selecionado. O CLI existente aceita
   `comunica --numero <CNJs> --interval 1`; `--numero` não pula consultados por si,
   portanto filtre antes de montar o lote. Não invente flags como `--manifest`
   para esse comando sem implementá-las e testá-las.
5. Complete primeiro os 200 do manifesto. A API pública já configurada é
   `https://comunicaapi.pje.jus.br/api/v1/comunicacao`, por número CNJ, paginada.
   Não é API de autos nem de inteiro teor. Mantenha intervalo de pelo menos
   um segundo e as retentativas limitadas existentes; não paralelize requisições.
   Não contorne CAPTCHA, 403, login ou bloqueios.
6. Se o lote terminar sem bloqueio e a persistência estiver correta, consulte
   **até mais 200 CNJs inéditos**, com quotas 100/50/50 nos mesmos grupos,
   estratificação por ano e assunto e manifesto salvo antes da coleta.
   Use semente explícita, exclua consultas anteriores e deduplique CNJs entre grupos.
   Não selecione só casos recentes para aumentar artificialmente a taxa de cobertura.
   Se uma quota não puder ser preenchida, documente; não mude o recorte silenciosamente.
7. Preserve respostas originais na Bronze e itens em `comunicacoes_pje`, conforme
   contrato. Deduplicação por processo/hash; mantenha positivos, vazios e erros
   distinguíveis. Não modifique extrações anteriores da IA.

## Medição e entrega

Crie `RELATORIO_AMPLIACAO_COMUNICA_20261008.md` na raiz contendo:

- Caminho do banco, backups, manifestos, IDs de coleta e método reproduzível.
- Por lote/grupo/ano: selecionados, consultados, encontrados, vazios, erros,
  pendentes; comunicações observadas versus efetivamente novas.
- Quantos CNJs possuem publicação rotulada sentença/decisão/acórdão,
  distinguindo rótulo publicado de conteúdo efetivamente verificado.
- Ganho líquido comparado às 110 comunicações anteriores, sem somar observações
  duplicadas ou confundir documento com processo.
- Revisão local de até dez textos novos desses tipos, sem divulgar nomes,
  CPF ou trechos pessoais no relatório. Diga se contêm fundamentação/dispositivo
  e se o motivo da negativa administrativa é explicitamente informado.
  Ausência de informação deve continuar ausência, não hipótese gerada pela IA.
- Limitações temporais/geográficas e se o ganho permite entender judicialização
  ou apenas atos processuais. Não extrapole resultados do lote à população inteira.
- Contagens finais, `PRAGMA integrity_check` e `foreign_key_check`, preservação
  das tabelas de processos/documentos/extrações e existência/leitura das Bronzes.
- Comando de retomada executável, com seleção explícita do SQLite e filtragem
  de pendentes, caso algo fique incompleto.

Atualize o Log de decisões de `docs/CONTRATOS.md` e a seção pertinente de
`docs/FONTES_ABERTAS.md` com números verificados. Sem schema novo nesta tarefa.
Se alterar código, acrescente testes e rode a suíte pertinente.

Textos ficam locais, fora do Git e **não são enviados à IpeaIA** nesta tarefa.
Não substitua o pacote de transferência nem o banco remoto: isso é outra etapa.
Finalize com resumo curto do ganho e dos limites, não com promessa de autos completos.
