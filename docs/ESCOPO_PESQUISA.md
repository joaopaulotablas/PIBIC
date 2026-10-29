# Recorte da pesquisa e fontes de dados

O [plano de pesquisa](../plano.txt) delimita o estudo a pedidos de **concessão**
de BPC/LOAS no TRF1, em Varas Federais e Juizados Especiais Federais com
competência sobre o Distrito Federal e a RIDE. Demandas de revisão de valor e
cessação ficam fora do corpus final.

## Seleção em etapas

1. **Candidatos:** consultar no DataJud os assuntos CNJ `6114`, `11946` e
   `11947`. A presença de um desses códigos não comprova, sozinha, que a ação
   seja de concessão de BPC.
2. **Recorte territorial inicial:** `TRF1` e município do **órgão julgador**
   `743` (Brasília no retorno observado do DataJud). Este filtro não identifica
   a residência da parte e não representa toda a RIDE.
3. **Instância inicial:** graus `G1` e `JE`. Registros `G2`/`TR` podem ser
   vinculados posteriormente para estudar recursos, sem duplicar ações na
   população de primeira instância.
4. **Inclusão final:** confirmar concessão de BPC e excluir revisão/cessação
   com regras explícitas e validação humana. O sistema ainda não implementa
   essa classificação; não usar os candidatos como denominador definitivo de
   taxa de procedência.

A RIDE inclui municípios de Goiás e Minas Gerais conforme a [lista oficial da
Sudeco](https://www.gov.br/sudeco/pt-br/acesso-a-informacao/perguntas-frequentes-1/RIDE).
Antes de estender o filtro territorial, é preciso mapear os códigos de município
do DataJud e a competência de cada Vara/JEF. Local do órgão e residência do
requerente são variáveis diferentes.

### Mapeamento oficial de jurisdição (07/10/2026)

A [Resolução Presi TRF1 13/2026 e anexo](https://www.trf1.jus.br/sjgo/noticias/trf1-publica-resolucao-que-consolida-a-jurisdicao-das-secoes-e-subsecoes-judiciarias-da-1a-regiao)
mostram municípios da RIDE/GO sob Anápolis, Formosa, Luziânia, Goiânia e
Uruaçu. Os valores crus do órgão DataJud observados nessas sedes são 216,
1798, 2788, 1903 e 5332, respectivamente; Brasília é 743. Para Minas Gerais,
os quatro municípios da RIDE (Arinos, Buritis, Cabeceira Grande e Unaí) estão
na jurisdição de Unaí/TRF6, cujo código DataJud observado é 3170404, conforme
a [jurisdição oficial TRF6](https://sjmg.trf6.jus.br/jurisdicoes/).

A consulta TRF1 retornou valores municipais de 3/4 dígitos mesmo no campo
`codigoMunicipioIBGE`; não convertê-los como códigos IBGE. TRF6 retornou para
Unaí o código IBGE de 7 dígitos. Consultas por código da sede recuperam
candidatos cuja Vara tem jurisdição sobre o entorno, mas não identificam a
residência da parte. Anápolis, Goiânia e Uruaçu estão fora da RIDE e devem
permanecer como grupo suplementar; Unaí/TRF6 também deve ficar separado do
estudo principal TRF1, até que a equipe confirme a ampliação do universo.

Consulta inicial reproduzível:

```powershell
docker compose run --rm ingestion datajud `
  --tribunais TRF1 --municipio-codigos 743 --graus G1 JE `
  --page-size 100 --max-records 1000
```

Para amostrar separadamente um dos três assuntos, acrescente `--assuntos 6114`
(ou `11946`/`11947`). A seleção de assuntos também integra o manifesto e gera
checkpoint próprio. O filtro pode ser escolhido no painel de coleta.

Para ampliar a cobertura temporal, use `--ano-ajuizamento 2023` (troque o ano
para cada estrato) junto com os filtros territoriais e de grau. O ano também
integra o manifesto e possui checkpoint independente. Uma meta operacional é
coletar um número comparável de candidatos por ano e por assunto, registrando
o total encontrado em cada estrato. A ordenação por `@timestamp` não sorteia
processos: mesmo estratificada, esta é uma **amostra de conveniência**, não
uma amostra aleatória representativa. Para estimar prevalências ou taxas,
será necessário conhecer os denominadores e definir pesos/desenho amostral.

Exemplo de continuação (sem `--restart`):

```powershell
docker compose run --rm ingestion datajud `
  --tribunais TRF1 --municipio-codigos 743 --graus G1 JE `
  --ano-ajuizamento 2022 --source-mode essencial `
  --page-size 20 --max-records 100
```

Execute os estratos em sequência, pois os checkpoints são gravados no mesmo
arquivo. O limite `--max-records` vale para a execução, não para o total
acumulado de um estrato. Consulte as contagens de processos **únicos** no banco;
registros de diferentes buscas podem se sobrepor.

O manifesto da consulta e o cursor `search_after` são específicos para o
conjunto de filtros. Para continuar, repita sem `--restart`; para recomeçar uma
mesma consulta do início, use `--restart`. Retire `--max-records` somente quando
o volume e a qualidade da amostra tiverem sido avaliados.

## Documentos e texto

O DataJud fornece capa e movimentações. O Comunica PJe pode acrescentar o texto
de alguns atos **publicados**, mas não o inteiro teor de todos os autos. Assim,
o banco atual não sustenta, por si só, inferências sobre perfil socioeconômico,
fundamentos jurídicos ou resultado da ação em toda a população. Essas extrações
exigem fonte documental apropriada, amostra anotada e validação antes das
métricas do plano.

O plano menciona e-Proc/TRF1 como origem das peças. O [portal atual do
TRF1](https://www.trf1.jus.br/trf1/processual/consulta-processual) direciona
as consultas de primeiro grau para **PJe**. Essa premissa precisa ser revista
antes de desenvolver um coletor de documentos. A consulta pública web não é
equivalente a uma API em lote de inteiro teor. O próprio [TRF1 explica](https://trf1.jus.br/trf1/noticias/?id=10392)
que a pesquisa pública mostra andamentos e atos, enquanto a visualização de
documentos exige acesso ao sistema. A [Resolução CNJ 185/2013, art. 27](https://atos.cnj.jus.br/atos/detalhar/1933)
prevê credenciamento para consulta remota ao inteiro teor no PJe.

## Avaliação do `mcp-juridico-brasil`

O [servidor MCP](https://github.com/DeHor-Labs/mcp-juridico-brasil) oferece
busca por número CNJ, movimentações, resumo assistido por modelo e monitoramento.
Segundo sua documentação, essas ferramentas usam a **API Pública do DataJud**.
Ele pode ser útil para inspeção e acompanhamento de casos conhecidos por um
assistente, mas não acrescenta uma fonte de peças, busca em lote por assunto ou
o recorte DF/RIDE. A ingestão reprodutível deve continuar consultando o
DataJud diretamente, preservando payload Bronze, manifesto e proveniência no
PostgreSQL. Não há motivo técnico para instalar o MCP como dependência da
pipeline neste momento.

### Atualização das fontes suplementares (07/10/2026)

A busca pública de inteiro teor do eproc/TRF6 foi integrada como fonte externa
suplementar: 20 decisões publicadas foram coletadas (10 TRF6, cinco TRU6 e cinco
Turmas Recursais). O eproc/TRF4 acrescentou 20 decisões BPC (10 TRF4, cinco TRU4
e cinco Turmas Recursais), e a pesquisa do eproc/TRF2 acrescentou 20 decisões
(10 TRF2, cinco TRU2 e cinco Turmas Recursais; não são casos do recorte DF/RIDE).
Nenhuma deve
ser assumida como processo do recorte DF/RIDE nem enviada a modelo externo antes
de revisão ética/privacidade. A consulta DataJud ao TJMG adicionou 361 registros de
Arinos, Buritis e Unaí; competência federal delegada e residência não foram
verificadas caso a caso. O lote Comunica PJe acrescentou 13 comunicações em 100
consultas, sem oferecer petições ou inteiro teor. DataJud TJGO acrescentou 4.513
processos (4.513 CNJs distintos nesta consulta) em órgãos estaduais de 29
municípios goianos da RIDE; competência delegada e residência não estão
confirmadas, então esse conjunto permanece suplementar e separado. O arquivo TRF1 está acessível
para documentos já publicados; não há API pública documentada de lote para os
autos das varas. A busca TRF3 continua indisponível nesta execução por timeout.
