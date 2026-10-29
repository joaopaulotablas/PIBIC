from __future__ import annotations

import gzip
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO


class BronzeWriter:
    """Grava respostas imutaveis em NDJSON gzip para auditoria e reprocessamento."""

    def __init__(self, root: str | Path, source: str, partition: str, run_id: str,
                 atomic_records: bool = False):
        day = datetime.now(timezone.utc).date().isoformat()
        self.path = Path(root) / source / partition.lower() / day / f"{run_id}.ndjson.gz"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file: TextIO | None = None
        self.atomic_records = atomic_records
        self._active = False

    def __enter__(self) -> "BronzeWriter":
        self._active = True
        if self.atomic_records:
            if self.path.exists():
                raise FileExistsError(f"Bronze existente preservada: {self.path}")
            with self.path.open("xb") as output:
                output.write(gzip.compress(b""))
            return self
        self._file = gzip.open(self.path, "at", encoding="utf-8")
        return self

    def write(self, document: Any) -> None:
        if self.atomic_records:
            if not self._active:
                raise RuntimeError("BronzeWriter precisa ser usado como context manager")
            payload = (json.dumps(document, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
            # Publish only complete gzip members. Killing the process before replace
            # leaves the previous canonical file intact; a temp file may remain.
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=self.path.parent, suffix=".partial", delete=False) as target:
                    temporary = target.name
                    with self.path.open("rb") as previous:
                        shutil.copyfileobj(previous, target)
                    target.write(gzip.compress(payload))
                    target.flush()
                    os.fsync(target.fileno())
                os.replace(temporary, self.path)
            finally:
                if temporary and os.path.exists(temporary):
                    os.unlink(temporary)
            return
        if self._file is None:
            raise RuntimeError("BronzeWriter precisa ser usado como context manager")
        self._file.write(json.dumps(document, ensure_ascii=False, separators=(",", ":")))
        self._file.write("\n")
        self._file.flush()

    def write_many(self, documents: list[dict[str, Any]]) -> None:
        for document in documents:
            self.write(document)

    def __exit__(self, *_: object) -> None:
        self._active = False
        if self._file is not None:
            self._file.close()
            self._file = None
