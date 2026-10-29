# Ingestão BPC

Este pacote é o núcleo de coleta do projeto. A execução oficial usa PostgreSQL
com pgvector pelo `compose.yaml` da raiz.

Comandos disponíveis:

```text
python -m bpc_ingestion datajud
python -m bpc_ingestion comunica
python -m bpc_ingestion importar-tpu
python -m bpc_ingestion resumo
python -m bpc_ingestion mds-censo-suas
```

Consulte o [README principal](../README.md) para instalação e exemplos.

`mds-censo-suas` baixa os arquivos públicos do Censo SUAS e guarda apenas
contagens de CRAS/Postos por município; não lê os CSVs de RH. Para adicionar os
agregados a uma cópia consolidada SQLite existente, use:

```text
python -m bpc_ingestion mds-censo-suas --storage sqlite --sqlite-path data/bpc-consolidado-luna-20261007.sqlite
```

O padrão continua usando PostgreSQL. O SQLite é compatibilidade/local e não
substitui o esquema analítico oficial.
