import gzip
import json
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from bpc_ingestion.bronze import BronzeWriter


class BronzeWriterTest(unittest.TestCase):
    def test_atomic_file_is_valid_before_close_and_after_failed_publish(self):
        with tempfile.TemporaryDirectory() as directory:
            with BronzeWriter(directory, "comunica_pje", "processos", "run", atomic_records=True) as writer:
                writer.write({"numero": 1})
                with gzip.open(writer.path, "rt", encoding="utf-8") as stream:
                    self.assertEqual([json.loads(x) for x in stream], [{"numero": 1}])
                with patch("bpc_ingestion.bronze.os.replace", side_effect=OSError("interrupted")):
                    with self.assertRaises(OSError):
                        writer.write({"numero": 2})
                with gzip.open(writer.path, "rt", encoding="utf-8") as stream:
                    self.assertEqual([json.loads(x) for x in stream], [{"numero": 1}])
                writer.write({"numero": 2})
            with gzip.open(writer.path, "rt", encoding="utf-8") as stream:
                self.assertEqual([json.loads(x) for x in stream], [{"numero": 1}, {"numero": 2}])

    def test_atomic_keyboard_interrupt_preserves_complete_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(KeyboardInterrupt):
                with BronzeWriter(directory, "comunica_pje", "processos", "run", atomic_records=True) as writer:
                    writer.write({"numero": 1})
                    raise KeyboardInterrupt()
            with gzip.open(writer.path, "rt", encoding="utf-8") as stream:
                self.assertEqual([json.loads(x) for x in stream], [{"numero": 1}])

    def test_writes_recoverable_gzip_ndjson(self):
        with tempfile.TemporaryDirectory() as directory:
            with BronzeWriter(directory, "datajud", "TRF1", "run-1") as writer:
                writer.write({"_id": "one", "texto": "beneficio"})
                path = writer.path
            self.assertTrue(path.exists())
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                self.assertEqual(
                    json.loads(stream.readline()),
                    {"_id": "one", "texto": "beneficio"},
                )


if __name__ == "__main__":
    unittest.main()
