import gzip
import json
from types import SimpleNamespace

import pytest

from bpc_ingestion import cli
from bpc_ingestion.comunica import PjeResult


@pytest.mark.parametrize("interrupt", [False, True])
def test_comunica_closes_failed_run_and_keeps_bronze(tmp_path, monkeypatch, interrupt):
    finished, saved = [], []
    class Store:
        def __init__(self, url): pass
        def start_collection(self, *args): return "run"
        def save_pje_result(self, *args): saved.append(args); return 0
        def finish_collection(self, *args): finished.append(args)
        def close(self): pass
    class Client:
        def __init__(self, *args, **kwargs): self.calls = 0
        def fetch_process(self, number):
            self.calls += 1
            if interrupt and self.calls == 2: raise KeyboardInterrupt()
            return PjeResult("erro_temporario", [], 5, 503, "Unavailable", [])
    monkeypatch.setattr(cli, "PostgresStore", Store)
    monkeypatch.setattr(cli, "ComunicaPjeClient", Client)
    args = SimpleNamespace(numero=["a", "b", "c", "d"], limit=4, interval=1)
    settings = SimpleNamespace(database_url="unused", comunica_base_url="unused", raw_data_dir=tmp_path)
    with pytest.raises(KeyboardInterrupt if interrupt else RuntimeError):
        cli.collect_comunica(args, settings)
    assert len(saved) == (1 if interrupt else 3)
    assert finished[-1][1] == "falhou"
    with gzip.open(finished[-1][3], "rt", encoding="utf-8") as stream:
        assert len([json.loads(x) for x in stream]) == len(saved)
