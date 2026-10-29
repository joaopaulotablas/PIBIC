import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from bpc_ingestion.corpus_audit import audit_database, inspect_item, main


def test_offsets_fields_hashes_and_no_context_export():
    text = 'Pessoa Privada tem renda familiar; citação: JULGO IMPROCEDENTE. CPF 123.456.789-00.'
    result = inspect_item('documento', dict(id=1, fonte='tnu', documento_id='abc',
                          hash_conteudo='payload-hash', texto=text, ementa=None, decisao=None), [9])
    assert result['hash_conteudo'] == 'payload-hash'
    assert result['campos']['texto']['sha256_texto'] == hashlib.sha256(text.encode()).hexdigest()
    assert 'renda' in result['pistas_lexicais']
    assert result['revisao_semantica'] == 'pendente'
    for occurrence in result['ocorrencias']:
        assert text[occurrence['inicio']:occurrence['fim']] == occurrence['expressao']
    assert 'Pessoa Privada' not in json.dumps(result)
    assert '123.456.789' not in json.dumps(result)
    assert 'resultado_judicial' not in result


def test_missing_text_ementa_only_and_binary_document():
    base = dict(id=1, fonte='stj', hash_conteudo='x', texto=None, ementa='LOAS', decisao=None)
    assert inspect_item('documento', base, [])['disponibilidade'] == 'espelho_ementa'
    base['ementa'] = '  '
    assert inspect_item('documento', base, [])['disponibilidade'] == 'sem_texto'


def test_readonly_complete_counts_duplicates_and_exclusive_output():
    with tempfile.TemporaryDirectory() as work:
        path = Path(work) / 'base.sqlite'
        c = sqlite3.connect(path)
        c.executescript('''
          CREATE TABLE documentos_publicos(id,fonte,documento_id,hash_conteudo,texto,ementa,decisao);
          CREATE TABLE documento_processos(documento_id,processo_id);
          CREATE TABLE comunicacoes_pje(id,processo_id,comunica_id,hash_conteudo,texto);
          INSERT INTO documentos_publicos VALUES(1,'tnu','x','a','LOAS renda familiar',NULL,NULL);
          INSERT INTO documentos_publicos VALUES(2,'tnu','x','b','LOAS renda familiar',NULL,NULL);
          INSERT INTO documento_processos VALUES(1,45);
          INSERT INTO comunicacoes_pje VALUES(1,45,'y','c','LOAS renda familiar');
        ''')
        c.commit()
        c.close()
        before = path.read_bytes()
        audit = audit_database(path)
        assert audit['total_itens'] == 3
        assert audit['por_fonte']['tnu']['identidades_origem'] == 1
        assert audit['textos_principais_distintos'] == 1
        assert len(audit['duplicatas_textuais'][0]['itens']) == 3
        assert path.read_bytes() == before
        out = Path(work) / 'audit.json'
        main(['--database', str(path), '--output', str(out)])
        with pytest.raises(ValueError):
            main(['--database', str(path), '--output', str(out)])
        with pytest.raises(ValueError):
            audit_database(Path(work) / 'missing.sqlite')
