# Correções e verificação de fontes — 08/10/2026

## Código e validação

- Minimização preserva expressões dispositivas antes das regex amplas de nomes,
  incluindo `JULGO IMPROCEDENTE`, `JULGO PROCEDENTE`, `JULGO PARCIALMENTE
  PROCEDENTE` e `EXTINGO`. Não é garantia de anonimização ou de integridade
  semântica de todo documento; revisão humana continua necessária.
- Validador rejeita resumo vazio, resumo acima de 1500 caracteres, lacunas
  fora de lista de textos e IDs booleanos. Importador rejeita processos
  duplicados/IDs não inteiros na entrada preparada.
- União remapeia também `evidencias[].comunicacao_id` pela origem e verifica
  processo e hash. Auditoria registra IDs original/destino. Comparação lógica
  normaliza essas identidades e as FKs das chaves de comunicação.
- Testes acrescentados para linguagem dispositiva, formatos inválidos,
  colisão de IDs, hash divergente, outra pessoa/processo e ordem inversa de
  consolidação. Suíte: **154 passaram**, dois avisos de depreciação existentes.
- Prévia corrigida local: `data/ipeaia_comunicacoes_corrigidas_20261008.json`,
  20 comunicações de sete processos. Prévia anterior preservada. Nenhuma chamada
  à IpeaIA nem extração artificial gravada; zero extrações IA locais.

## Coleta e investigação

- TRF6 LOAS, cinco URLs novas: cinco documentos/versões acrescentados. Banco
  explicitamente selecionado: `data/bpc-consolidado-luna-20261007.sqlite`.
  173 documentos públicos, 16.737 processos, 220 comunicações, quatro vínculos.
  Corpus suplementar não cria população nem comprova concessões iniciais DF/RIDE.
- TRF3 documento 344467700: HTML confirmado na pesquisa web, mas download direto
  expirou em 25 segundos. Coleta `falhou`, zero documentos novos dessa fonte.
- SJPA indica oficialmente inteiro teor na consulta processual por vara.
  Investigação do formulário legado expirou em 20 segundos; não consultou
  processo nem importou documentos. Não extrapolar o serviço do Pará para DF.
- Endpoints e limites documentados em `docs/FONTES_ABERTAS.md`.

## Transferência

Pacote novo, sem sobrescrever o anterior:
`transferencia/bpc-consolidado-luna-20261008-corrigido.sqlite.gz`, 59,2 MiB.
SHA-256: `29bf3f441ad867a56844f299f3abf87deaa9ca5331951c0a161315532ee5197d`.

Exportador conferiu todas as 19 tabelas; teste real de inicialização em destino
temporário novo concluiu com integridade e FKs válidas. Exceção Git exata só
para o pacote corrigido; outros pacotes de trabalho, Bronze e diagnósticos
continuam ignorados. Sem commit/push automático. Textos públicos podem conter
dados pessoais; publicação aberta não equivale à transferência controlada.

Guia atualizado: `GUIA_TRANSFERENCIA_BPC_CONSOLIDADO.md`. Preserve snapshot do
banco remoto e consolide suas extrações antes de selecionar o banco novo.
O pacote não é sincronização automática: coletas futuras exigem novo snapshot.
