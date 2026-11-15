# Coleta dirigida PJe/TRF1 — lote inicial em cópia isolada

Execução de 29/10/2026, em cópia independente do SQLite indicado para esta
frente. O banco original permaneceu somente leitura. O lote terminou após o
primeiro candidato processado, quando o validador detectou divergência de
identidade no cabeçalho de um documento; a coleta não foi contornada nem
retomada com heurísticas.

## Universo e seleção

O backup SQLite foi criado por `sqlite3.Connection.backup` a partir de
`data/bpc-consolidado-luna-20261007.sqlite` para
`data/amostragem-inicial/coleta-pje-20261029-210636.sqlite`. O backup passou
`quick_check` antes da coleta. No snapshot, os denominadores elegíveis TRF1,
graus G1/JE, assuntos CNJ 6114/11946/11947 e município do órgão julgador foram:

| Código do município do órgão | Elegíveis no snapshot | Selecionados no manifesto |
| --- | ---: | ---: |
| 743 — Brasília | 1.793 | 20 |
| 1798 — Formosa | 1.031 | 20 |
| 2788 — Luziânia | 999 | 20 |
| **Total** | **3.823** | **60** |

Os códigos identificam a sede do órgão julgador, não a residência de partes.
O manifesto completo, com os CNJs necessários para retomada, está em
`data/amostragem-inicial/manifesto-pje-20261029.json` e deve permanecer local.
O coletor selecionou candidatos ainda sem estado concluído/sem resultado/sem
documentos, alternando os três estratos. A seleção não é amostra aleatória da
população.

## Resultado real

O CLI utilizado foi o `python -m bpc_ingestion.pje_public` existente, com o
manifesto, limite de 60 casos, até 10 documentos por processo, timeout de 25 s
e intervalo fixo de 1 s entre requisições. A primeira execução falhou na
conexão antes de qualquer resposta e foi registrada como falha na cópia. Na
tentativa seguinte, o portal público respondeu sem exigir autenticação nem
CAPTCHA. O coletor salvou 7 respostas HTML comprimidas na Bronze local,
parseou 3 documentos e interrompeu ao detectar divergência de identidade no
cabeçalho do documento seguinte. Entre os 60 selecionados, 1 chegou à consulta
e terminou com falha de validação, 59 não foram consultados, e nenhum terminou
com `sem_resultado`, `sem_documentos` ou estado `bloqueada` nesta execução.

Os três documentos parseados eram duplicatas já presentes no snapshot: uma
decisão e dois despachos, todos já vinculados ao processo correspondente.
Foram observados 3 documentos, 0 documentos novos e 0 vínculos novos. Nenhum
processo foi criado. A validação incorreta foi preservada como `falhou`; nenhum
documento não validado foi associado. A execução teve 2 tentativas para o mesmo
candidato (erro de conexão inicial e divergência documental na tentativa que
chegou à fonte). Não houve tentativa de repetir o candidato ou continuar o lote
depois da divergência.

No snapshot final, `coletas` para `pje_trf1_publico` registra 827 concluídas,
73 sem documentos e 54 falhas (incluindo as duas tentativas desta frente).
Esses números são estados de tentativas e não contagens de processos únicos.
O corpus PJe da cópia contém 2.281 documentos e 2.281 vínculos explícitos.

## Integridade e privacidade

Após a gravação, `PRAGMA foreign_key_check` retornou zero violações e
`PRAGMA quick_check` retornou `ok`. A revisão de vínculo confirma que os três
documentos parseados correspondem a versões já vinculadas ao processo; a
divergência posterior permaneceu sem vínculo novo. O arquivo original não foi
aberto para escrita e nenhuma outra cópia de amostragem foi alterada.

HTML bruto, manifesto com CNJs e banco ficam em `data/amostragem-inicial/` para
consolidação posterior. O relatório omite CNJs, IDs documentais, conteúdo dos
autos e mensagens que possam conter dados pessoais. Os arquivos brutos podem
conter dados pessoais e devem continuar no ambiente local, sem publicação.

## Verificação

Executado `python -m pytest tests/test_pje_public.py -q` em `ingestion/`:
**18 testes passaram**. O teste cobre os limites do formulário público, a
detecção de CAPTCHA, a validação de URLs oficiais, os estados de consulta e as
identidades processuais/documentais.

O lote solicitado de até 60 casos terminou com 1 processo consultado e 59
selecionados ainda não consultados. A cópia e o manifesto ficam disponíveis
para consolidação ou para uma retomada deliberada após revisão humana do caso
que causou a divergência; a evidência não confirma concessão inicial de BPC,
residência, nem resultado jurídico.
