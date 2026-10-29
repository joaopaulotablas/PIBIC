# Guia de transferencia do SQLite consolidado Luna

Pacote novo, gerado a partir de `data/bpc-consolidado-luna-20261007.sqlite`,
com banco SQLite explicitamente selecionado. A exportacao nao le o PostgreSQL
configurado em `.env`:

- Arquivo: `transferencia/bpc-consolidado-luna-20261008-corrigido.sqlite.gz`
- SHA-256: `29bf3f441ad867a56844f299f3abf87deaa9ca5331951c0a161315532ee5197d`
- 19 tabelas; 16.737 processos; 16.796 registros DataJud; 907.521 movimentos;
  220 comunicacoes; 841 consultas PJe; 173 documentos publicos; 4 vinculos;
  0 extracoes de IA.
- Copia descompactada: `PRAGMA integrity_check = ok`; nenhuma violacao FK.

O banco inclui textos publicados que podem conter dados pessoais. Esta pronto
para transferencia controlada ao servidor autorizado, mas exige revisao de
privacidade antes de qualquer publicacao aberta. Bronze, logs e diagnosticos nao
fazem parte do pacote. Por solicitação do pesquisador, o `.gitignore` permite
somente este pacote datado para transferência via Git; demais pacotes continuam
ignorados. Não houve commit ou push automático. Publicar em repositório aberto
também divulga os textos e eventuais dados pessoais, mesmo sendo documentos públicos.

## Levar pelo Git

Na origem, depois de conferir o conteúdo e a visibilidade do repositório:

```powershell
git add transferencia/bpc-consolidado-luna-20261008-corrigido.sqlite.gz
git commit -m "Pacote consolidado para pesquisa"
git push origin main
```

No servidor remoto, execute `git pull` e siga as etapas abaixo. O pull sozinho
não troca o banco em uso. Preserve e consolide as extrações remotas antes de
alterar `DATABASE_URL`. Os comandos acima adicionam somente o pacote, não
o submódulo nem arquivos Bronze. A exportação permanece o snapshot de 08/10;
coletas posteriores não entram nele automaticamente.

## Instalar sem Docker

Transfira o arquivo por canal aprovado e confira o hash no PowerShell:

```powershell
Get-FileHash transferencia/bpc-consolidado-luna-20261008-corrigido.sqlite.gz -Algorithm SHA256
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install ./ingestion
```

Inicialize em um caminho novo. O inicializador recusa sobrescrita e valida
integridade e FKs antes de criar a copia descompactada:

```powershell
.\.venv\Scripts\python.exe -m bpc_ingestion.portable inicializar `
  --package transferencia/bpc-consolidado-luna-20261008-corrigido.sqlite.gz `
  --output data/bpc-consolidado-luna-20261008-corrigido.sqlite
```

Selecione-o em `.env` (ou no ambiente do processo):

```dotenv
DATABASE_URL=sqlite:///./data/bpc-consolidado-luna-20261008-corrigido.sqlite
```

Execute o painel a partir da raiz do projeto. Confira `$env:DATABASE_URL` e
`python -m bpc_ingestion resumo`. Nao use um valor PostgreSQL de outro ambiente
para exportar este pacote.

## Preservar e consolidar extracoes remotas

Antes de selecionar outro banco, confirme que `data/bpc-remote.sqlite` e o
arquivo SQLite realmente usado no servidor. O exemplo cria snapshot via API de
backup SQLite e para sem sobrescrever um snapshot anterior:

```powershell
if (Test-Path data/bpc-remote-snapshot.sqlite) { throw 'Snapshot ja existe' }
.\.venv\Scripts\python.exe -c "import sqlite3; s=sqlite3.connect('file:data/bpc-remote.sqlite?mode=ro',uri=True); d=sqlite3.connect('data/bpc-remote-snapshot.sqlite'); s.backup(d); d.close(); s.close()"
.\.venv\Scripts\python.exe -c "import sqlite3; c=sqlite3.connect('file:data/bpc-remote-snapshot.sqlite?mode=ro',uri=True); print('extracoes_ia:',c.execute('select count(*) from extracoes_ia').fetchone()[0]); print('integrity:',c.execute('pragma integrity_check').fetchone()[0]); c.close()"
```

Guarde o snapshot e confirme a contagem e a origem das extracoes. Nao
inicialize por cima de `data/bpc-remote.sqlite` nem apague extracoes antigas.
Para consolidar o snapshot primeiro e o pacote novo depois, gere um destino
novo (o `.gz` e lido sem alteracao):

```powershell
.\.venv\Scripts\python.exe scripts\consolidate_databases.py `
  --sqlite data/bpc-remote-snapshot.sqlite `
  --sqlite transferencia/bpc-consolidado-luna-20261008-corrigido.sqlite.gz `
  --output data/bpc-consolidado-preservado-20261008.sqlite `
  --report data/consolidacao-remota-20261008.json
```

A ordem preserva as extracoes existentes primeiro; comunicações e demais
identidades do pacote sao acrescentadas ou deduplicadas. O consolidador remapeia
FKs e referencias `registro_id` e `comunicacao_id` das evidencias. Antes de selecionar a saida,
revise conflitos, contagem/conteudo de `extracoes_ia`, integridade e FKs.
Conflitos logicos nao sao mesclados por heuristica; resultados divergentes
exigem revisao humana. So entao altere `DATABASE_URL` para o destino consolidado.
Guarde snapshot e relatorio.
