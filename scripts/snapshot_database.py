"""Create a consistent, read-only SQLite snapshot from configured application DB."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

from bpc_ingestion.database import make_engine
from bpc_ingestion.portable import copy_database


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    load_dotenv(".env", override=False)
    raw_url = os.getenv("DATABASE_URL")
    url = raw_url or URL.create(
        "postgresql+psycopg", username=os.getenv("POSTGRES_USER", "bpc"),
        password=os.getenv("POSTGRES_PASSWORD", "bpc"), host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")), database=os.getenv("POSTGRES_DB", "bpc"),
    )
    source = make_engine(url, pool_pre_ping=True)
    try:
        counts = copy_database(source, args.output)
        print(f"Snapshot criado: {args.output}; tabelas={len(counts)}; processos={counts.get('processos', 0)}")
    finally:
        source.dispose()


if __name__ == "__main__":
    main()
