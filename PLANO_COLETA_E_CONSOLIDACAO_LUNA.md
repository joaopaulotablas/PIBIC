# Plano de execução — consolidação e conteúdo processual BPC

Este arquivo é o briefing para o agente Luna executar no repositório PIBIC.
Leia o plano inteiro antes de começar. O objetivo é reunir os dados já coletados
e obter conteúdo documental dos casos da pesquisa, com cobertura mensurável.

## 1. Objetivo e autorização

O usuário autorizou investigar fontes públicas e seguir a recomendação de
consolidar os bancos e priorizar documentos dos processos existentes.
Implemente, teste e execute pilotos locais. Não fique apenas propondo mudanças.
O presente arquivo é um plano: sua criação não executou a consolidação ou novas coletas.

Comece lendo `docs/CONTRATOS.md`, `plano.txt`, `docs/ESCOPO_PESQUISA.md`,
`docs/FONTES_ABERTAS.md` e quaisquer `AGENTS.md` aplicáveis.
`docs/CONTRATOS.md` é a fonte da verdade dos schemas e decisões.
Atualize esse contrato antes de criar ou alterar um schema de persistência.

O projeto estuda concessão inicial de BPC/LOAS no DF/RIDE, com recorte TRF1
definido pelo plano. Revisão e restabelecimento/cessação ficam fora do objetivo
principal. Registros de TRF6/Unaí e de tribunais estaduais devem permanecer
identificados como candidatos suplementares, até decisão metodológica explícita.
Sede do órgão julgador não comprova residência da parte.
Na TPU local, 11946 e 11947 descendem de 6114; use a hierarquia, não apenas os
rótulos isolados “Deficiente” e “Idoso”, para avaliar o vínculo temático.

Preserve todas as alterações existentes no worktree, inclusive os coletores
novos ainda não rastreados pelo Git. Não modifique nem faça commit no submódulo
`jeferson/bpc-loas`. Não faça push nem commit sem pedido específico.
Credenciais vêm do ambiente e nunca devem aparecer nos logs, relatórios ou Git.

## 2. O que existe e o que continua faltando

Estas contagens foram verificadas em 07/10/2026 e são uma referência, não uma
assertiva sobre a máquina onde você executará. Faça nova auditoria inicial.

| Dado | PostgreSQL configurado | `data/bpc-remote.sqlite` local |
| --- | ---: | ---: |
| Processos | 7.097 | 12.224 |
| Registros DataJud | 7.101 | 12.283 |
| Versões de documentos públicos | 41 | 105 |
| Comunicações publicadas | 42 | 55 |
| Vínculos documento–processo | 0 | 3 |

PostgreSQL: 20 documentos TRF2, 20 TRF4 e 1 espelho STJ.
SQLite: 11 versões CJF/TRF1, 21 STJ, 30 TNU, 7 arquivo TRF1, 16 TRF5 e 20 TRF6.
As três associações documentais do SQLite pertencem ao mesmo processo do Piauí,
fora do recorte DF/RIDE. Elas não representam cobertura textual de três casos.
O SQLite local tinha zero extrações em `extracoes_ia`; isso não prova ausência
de extrações na máquina remota do pesquisador.

O PostgreSQL recebeu 4.513 candidatos TJGO. O SQLite recebeu ampliação federal
e 361 registros TJMG. Os conjuntos se sobrepõem e não podem ser somados.
Os 60 documentos TRF2/TRF4/TRF6 são material complementar; não foram ligados
automaticamente aos casos da pesquisa.

A triagem IpeaIA atual envia DataJud + TPU e salva `resumo_caso` em português
no JSON de `extracoes_ia`, prompt v1.2. Ela ainda não interpreta documentos
dessas fontes. Só metadados normalmente deixam motivo e desfecho indeterminados.

IpeaJus: a nota técnica de 2018 demonstra uso histórico de microdados,
diários e sentenças. Não fornece uma API, um download da base ou acesso atual.
Trate-o como pista para investigação, nunca como integração disponível.

## 3. Ordem de execução

Execute P0, depois P1. Execute P2 se P1 atingir o piloto ou se as fontes do
recorte ficarem bloqueadas. P3 é uma expansão contextual, de menor prioridade.
Um bloqueio numa fonte não deve impedir o trabalho independente nas demais.

### P0 — Auditar e consolidar os dados existentes

1. Identifique o banco apontado por `DATABASE_URL`, os arquivos SQLite e os
   pacotes em `transferencia/`. Não imprima a URL com usuário/senha.
2. Registre contagens por tabela, tribunal e fonte, documentos distintos e
   versões, vínculos, extrações, datas de coleta e estados das coletas.
   Verifique também se os arquivos Bronze referenciados realmente existem.
3. Faça backups com nomes novos e registre seus caminhos e hashes. Leia os
   bancos originais sem alterá-los. Caso a cópia do ambiente remoto com
   extrações recentes não esteja aqui, registre essa ausência; preserve um
   caminho posterior de importação dessas extrações.
4. Implemente uma consolidação em arquivo SQLite NOVO, por exemplo
   `data/bpc-consolidado-<data-hora>.sqlite`. A primeira execução deve oferecer
   `--dry-run`; nunca substitua `data/bpc-remote.sqlite` ou restaure o
   PostgreSQL automaticamente.
5. Use o schema da aplicação (`models.py`, `database.py`, `portable.py`).
   `SqliteStore`/`processos_raw` são legado e não equivalem ao banco analítico.
   `portable.copy_database` copia um banco; não é um algoritmo de união.
6. Faça a união por identidades lógicas previstas no contrato, com remapeamento
   de todos os IDs e FKs. IDs numéricos iguais entre bancos não indicam a mesma
   entidade. Percorra dependências em ordem e mantenha mapas origem → destino.
   Preserve UUIDs/identidades operacionais quando possível e trate colisões
   divergentes explicitamente.
7. Deduplicate processos por CNJ; registros DataJud por índice + ID quando
   presentes; documentos por fonte + documento_id + hash; comunicações e
   extrações conforme suas chaves contratuais. Inspecione a representação real
   dos registros SQLite antes de definir o pareamento: nunca invente um ID
   DataJud que esteja ausente. Registros ambíguos precisam de relatório.
8. Para entidades mutáveis, diferencie duplicata idêntica de atualização e
   conflito. Preserve versões documentais, resultados de IA e evidências;
   não sobrescreva conteúdo divergente silenciosamente. Documente a política
   de atualização e reporte conflitos com referências às duas origens.
9. Preserve associação às coletas, hashes e referências Bronze. Um arquivo
   ausente deve aparecer como indisponível, não como documento recuperável.
10. Valide FK, integridade SQLite, unicidade, contagens por origem e o carregamento
    de alguns processos/documentos no painel. Cada registro de origem deve
    corresponder a um registro preservado, a uma duplicata demonstrada ou a
    um conflito reportado. Quantifique a cobertura dessa correspondência.

Adicione testes pequenos e significativos: IDs locais colidentes com CNJs
diferentes; mesmo CNJ com registros distintos; documento repetido versus nova
versão; vínculos remapeados; extrações preservadas; indicador duplicado sem
somar snapshots; recusa de saída já existente. Repita a união das mesmas
entradas em outro arquivo novo e compare identidades e conteúdo normalizado,
não bytes SQLite ou IDs locais.

Conclua P0 com um banco consolidado validado e relatório. Não promova a cópia
nova à base usada pelo pesquisador nem exporte um pacote incompleto para Git.
Inclua os comandos de uso/transferência e os arquivos Bronze necessários.
Se uma origem não estiver disponível, entregue consolidação parcial claramente
rotulada e a pendência exata.

### P1 — Buscar documentos dos processos da própria amostra

1. Gere um manifesto de candidatos do banco consolidado: CNJ, tribunal, grau,
   órgão, assuntos com hierarquia, ano e motivo de inclusão no piloto.
   Identifique separadamente núcleo TRF1/DF, candidatos de subseções da RIDE
   e grupos suplementares. Não selecione apenas processos já encerrados ou
   com resultado favorável.
2. Selecione 50 casos de forma reproduzível, distribuídos por ano, órgão e
   assunto quando possível. Registre semente, método e distribuição efetiva.
   Consulte todos os selecionados, inclusive tentativas sem resultado.
3. Reutilize os coletores existentes para procurar publicações pelo CNJ:
   - `comunica.py`: comunicações/atos públicos, não autos completos;
   - `public_sources.py`: pesquisa CJF/TRF1/JEF1 e arquivo TRF1;
   - `archive_text.py`: conversão dos DOC já obtidos.
4. Audite as limitações de seleção de `cjf-amostra`: hoje a escolha automática
   é restrita a Brasília. Para os CNJs restantes do piloto, implemente seleção
   explícita/manifesto ou extensão documentada do comando. Não use os padrões
   dos comandos como se já selecionassem exatamente o piloto planejado.
5. Confirme os hosts e as rotas oficiais atuais. Diferencie o serviço público
   de publicações de qualquer API institucional chamada Comunica PJe. Não
   suponha que um endpoint de comunicações forneça peças completas.
6. Investigue os diários oficiais históricos do TRF1 e suas seções: navegue por
   links publicados no portal oficial, identifique acervo, intervalo temporal,
   formato PDF/HTML, termos de uso e possibilidade de download público.
   Comece com poucas edições próximas a datas de atos do piloto. Não invente
   URLs ou IDs. Se viável, implemente descoberta, download e extração local.
7. Em diários, uma página pode conter vários processos. Segmente por cabeçalhos
   e limites verificáveis, preserve edição/página/trecho e evite associar uma
   sentença ao CNJ apenas citado como precedente. Uma referência isolada ao
   CNJ não prova identidade do processo do documento.
8. Preserve o original antes do parsing e salve conteúdo, tipo, fonte, data,
   URL, hash e coleta conforme contrato. Se precisar de campos de página ou
   localização de evidência, defina sua representação no contrato primeiro.
9. Registre por fonte: encontrado, sem resultado, erro e bloqueio. CAPTCHA
   exige interrupção dessa fonte. Não contorne autenticação ou anti-robô.
   `sem_resultado` não significa ausência de documentos nos autos.
10. Revise manualmente até 10 documentos positivos, ou todos se houver menos:
    CNJ, tipo, corte de texto, completude aparente e fatos sustentados.
    Diferencie petição, sentença, acórdão, despacho, intimação e ementa.

Relatório obrigatório do piloto: número de CNJs consultados, casos com alguma
publicação, com sentença/decisão, com motivo administrativo explícito e com
desfecho verificável. Mostre numeradores e denominadores; não chame nenhum
deles de taxa de procedência. Relate distribuição dos erros e diferenças
por ano/órgão. Não force o preenchimento de motivo/perfil com inferências.

Se o piloto tiver vínculos corretos e execução estável, avance a 200 casos
com o mesmo método. Se não houver resultados ou houver bloqueio persistente,
registre a evidência e prossiga com P2; não exija sucesso artificial.

### P2 — Ampliar corpus complementar e investigar acesso institucional

**Portais que já funcionaram:** TNU e TRF2/TRF4/TRF5/TRF6. Amplie em lotes
pequenos, começando com até 20 URLs por fonte e limite total de 100 URLs nesta
etapa. Use termos específicos BPC/LOAS/benefício assistencial, registre a
consulta e confira relevância. Resultados são seleção de jurisprudência,
não amostra representativa dos processos de concessão inicial DF/RIDE.

**STJ:** antes de repetir coleta grande, diagnostique a demora por etapa:
importação/configuração, conexão ao banco, criação de tabelas, catálogo,
download, parsing e gravação. Houve um documento salvo e execuções interrompidas;
não há prova de que a causa seja rede Python. Compare `curl` e o cliente Python
no MESMO recurso, registre duração/status e use testes com timeout. Não
imprima cookies ou tokens. Corrija a causa demonstrada; adicione logs de avanço
e finalize coletas interrompidas com status e contagem real. Teste um conjunto
e um recurso antes de aumentar o lote. Espelho não é inteiro teor de sentença.

**TRF3:** confirme a consulta oficial e teste uma tentativa limitada. Timeouts
anteriores não demonstram inexistência de consulta pública. Um novo coletor
exige resposta real, layout observado e testes; pare se continuar inacessível.

**TJMG/TJGO:** prioridade inferior aos documentos federais. Há candidatos
DataJud, mas competência delegada e residência ainda não foram verificadas.
No TJMG, a pesquisa web anterior retornou desafio CAPTCHA. Não automatize sua
resolução. Preserve esses candidatos para validação metodológica.

**IpeaJus e cooperação:** pesquise páginas oficiais, repositórios e publicações
do Ipea para localizar eventual catálogo, pacote, código ou contato responsável.
Documente o que existe hoje e a evidência. Se não houver acesso público,
prepare um texto curto de solicitação ao responsável/orientador: recorte,
variáveis, período, documentos desejados e finalidade acadêmica. Prepare também
um rascunho de pedido de dados ao TRF1 caso seja necessário. Não envie e-mail,
protocole LAI ou represente o usuário sem autorização específica.
Não prometa acesso: a referência histórica de 2018 não comprova disponibilidade.

### P3 — Contexto administrativo, depois da cobertura documental

Amplie INSS indeferimentos/concessões para uma série de competências disponíveis
no catálogo oficial, começando com 3 meses e DF/GO/MG. Justifique essa seleção
e diferencie UF inteira de municípios da RIDE. Reutilize agregadores existentes,
sem somar snapshots diferentes da mesma competência. Para contexto municipal,
avalie os indicadores BPC/CGU já integrados e estatísticas públicas IBGE.

Use agregados para contextualizar região e período. Não atribua motivo INSS,
perfil censitário ou recebimento do benefício a uma pessoa/processo por
coincidência de município ou data. Não há vínculo individual demonstrado.

## 4. Comandos existentes para pilotos

Execute na raiz. Antes, verifique instalação e `--help`. Inspecione `DATABASE_URL`
sem exibir segredo e aponte as mutações à cópia de trabalho validada. O nome
`PostgresStore` sozinho não prova incompatibilidade com SQLite: confira
`database.py` e execute os testes relevantes no backend escolhido.

```powershell
.\.venv\Scripts\python.exe -m bpc_ingestion --help
.\.venv\Scripts\python.exe -m bpc_ingestion comunica --numero <CNJ_DO_MANIFESTO> --interval 1
.\.venv\Scripts\python.exe -m bpc_ingestion cjf-amostra --limit 10 --base JEF1 --paginas 2 --timeout 120
.\.venv\Scripts\python.exe -m bpc_ingestion arquivo-trf1 --numero <CNJ_DO_MANIFESTO> --baixar --limite-documentos 5 --timeout 60
.\.venv\Scripts\python.exe -m bpc_ingestion converter-arquivo-trf1 --limit 10
.\.venv\Scripts\python.exe -m bpc_ingestion converter-arquivo-trf1 --limit 10 --executar
.\.venv\Scripts\python.exe -m bpc_ingestion tnu-pesquisa --query LOAS --limit 20 --paginas 10 --timeout 120
.\.venv\Scripts\python.exe -m bpc_ingestion trf2-pesquisa --query BPC --origens TRF2 --limit 20 --paginas 10 --timeout 120
.\.venv\Scripts\python.exe -m bpc_ingestion trf4-pesquisa --query BPC --origens TRF4 --limit 20 --paginas 10 --timeout 120
.\.venv\Scripts\python.exe -m bpc_ingestion trf5-pesquisa --query LOAS --limit 20 --paginas 10 --timeout 120
.\.venv\Scripts\python.exe -m bpc_ingestion trf6-pesquisa --query BPC --origens TRF6 --limit 20 --paginas 10 --timeout 120
.\.venv\Scripts\python.exe -m bpc_ingestion documentos-publicos --fonte stj --conjuntos espelhos-de-acordaos-segunda-turma --recursos 1 --limit 20 --timeout 60
.\.venv\Scripts\python.exe -m pytest ingestion/tests -q
git diff --check
```

Os comandos de coleta gravam dados; não são previews. Os limites de busca de
jurisprudência contam URLs, e uma URL pode conter vários documentos. Os comandos
acima são alternativas por etapa, não uma sequência para copiar cegamente.
Não use `--restart`/`--retentar` por padrão. Faça testes proporcionais às mudanças.
Se um processo travar, diagnostique antes de repetir e confira se deixou uma
coleta `executando`; só finalize uma execução órfã após confirmar que parou.

## 5. Preparação para a IA

Esta execução prepara dados, não amplia automaticamente o envio de documentos
à API IpeaIA. Respeite o tratamento local e a revisão definidos no plano do
projeto e no contrato. Preserve extrações existentes do ambiente remoto.

Entregue um conjunto local de exemplos documentados para revisão: CNJ, fonte,
tipo, trecho que descreve pedido/motivo/desfecho e lacunas. Uma sentença pode
relatar o pedido ou a negativa administrativa; marque isso como relato da
sentença, sem afirmar que a petição original foi obtida.

Caso seja preparada uma futura entrada documental para IA, descreva-a em
documento separado: evidência com ID/hash do documento e localização, motivo,
pedido, argumentos, desfecho e resumo natural. Versione esse contrato antes de
implementar persistência. `resumo_caso` atual já existe; resumo mais fluente
não substitui evidência documental. Dados indisponíveis ficam indeterminados.

## 6. Entrega e critérios de conclusão

Crie `RELATORIO_EXECUCAO_COLETA_LUNA.md` na raiz com:

- bancos auditados, backups, destino consolidado e comandos de reprodução;
- registros preservados, duplicatas, conflitos e arquivos Bronze ausentes;
- integridade, testes relevantes e política de união aplicada;
- manifesto do piloto e cobertura por CNJ/fonte/tipo de documento;
- novos documentos e vínculos corretos, separados de versões e de processos;
- fontes bloqueadas, evidência do bloqueio e dependências do pesquisador;
- disponibilidade comprovada ou não do IpeaJus;
- limitações para motivo, perfil e resultado, e próxima etapa recomendada.

Atualize `docs/CONTRATOS.md` (incluindo Log de decisões),
`docs/FONTES_ABERTAS.md` e instruções de execução que mudarem.
O sucesso mínimo é uma união validada das origens disponíveis e um piloto
documental executado com resultados positivos/negativos auditáveis. Não é
necessário obter documentos onde não há acesso viável, mas é necessário
distinguir bloqueio, erro e ausência de resultado.

Finalize com uma resposta curta: o que foi incorporado, em qual banco, quantos
casos agora têm evidência documental útil e o que depende de acesso adicional.
Não declare que resolveu a interpretação dos casos apenas por aumentar contagens.

## 7. Referências de partida

- Contrato e fontes do próprio repositório, citados acima.
- TRF1, pesquisa de jurisprudência e fonte JEF:
  https://www.trf1.jus.br/trf1/carta-servicos/jurisprudencia
- Arquivo público de documentos publicados: https://arquivo.trf1.jus.br/
- TNU: https://eproctnu-jur.cjf.jus.br/eproc/
- Catálogo STJ: https://dadosabertos.web.stj.jus.br/group/jurisprudencia
- Catálogo INSS: https://dadosabertos.inss.gov.br/
- Nota Técnica Ipea nº 9/2018, referência histórica do IpeaJus:
  https://portalantigo.ipea.gov.br/agencia/images/stories/PDFs/nota_tecnica/181220_NT_9_Astec.pdf

Valide links/redirecionamentos e disponibilidade na execução. Não trate as
referências como promessa de API ou acesso integral aos autos.
