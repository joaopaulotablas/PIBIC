import sqlite3
import unittest

from sample_initial import load, select


def row(cnj, site='Brasília/DF'):
    return {'cnj': cnj, 'sede': site, 'assunto_estrato': '11946', 'ano': '2023', 'presenca_decisao': True, 'tipos': 'Sentença'}


class SampleTests(unittest.TestCase):
    def test_determinism_limits_and_uniqueness(self):
        rows = [row(str(i), str(i % 3)) for i in range(100)]
        self.assertEqual(select(rows, 40, 42), select(list(reversed(rows)), 40, 42))
        self.assertEqual(len(select(rows, 200, 42)), 100)
        self.assertEqual(select(rows, 0, 42), [])
        with self.assertRaises(ValueError): select(rows, -1, 42)
        with self.assertRaises(ValueError): select(rows + [rows[0]], 10, 42)

    def test_filters_and_document_link(self):
        c = sqlite3.connect(':memory:')
        c.executescript('''CREATE TABLE referencias_tpu(tipo,codigo,codigo_pai); INSERT INTO referencias_tpu VALUES('assunto',11946,6114);
        CREATE TABLE processos(id,numero_processo); CREATE TABLE registros_datajud(id,processo_id,grau,orgao_codigo,orgao_nome,payload,data_ajuizamento,tribunal,nivel_sigilo);
        CREATE TABLE registro_assuntos(registro_id,assunto_codigo); CREATE TABLE assuntos(codigo,nome);
        CREATE TABLE documento_processos(processo_id,documento_id,criterio); CREATE TABLE documentos_publicos(id,documento_id,hash_conteudo,tipo_documento,numeros_cnj,fonte);
        INSERT INTO processos VALUES(1,'cnj1'),(2,'cnj2'),(3,'cnj3'); INSERT INTO assuntos VALUES(11946,'deficiência');
        INSERT INTO registros_datajud VALUES(1,1,'G1',1,'vara','{"orgaoJulgador":{"codigoMunicipioIBGE":743}}','2023','TRF1',0),
        (2,2,'G1',1,'vara','{"orgaoJulgador":{"codigoMunicipioIBGE":743}}','2023','TRF1',1),
        (3,3,'G1',1,'vara','{"orgaoJulgador":{"codigoMunicipioIBGE":743}}','2023','TRF1',0);
        INSERT INTO registro_assuntos VALUES(1,11946),(2,11946),(3,11946);
        INSERT INTO documentos_publicos VALUES(1,'id','hash','Despacho','["cnj1"]','pje_trf1'),(2,'id2','hash','Sentença','["outro"]','pje_trf1');
        INSERT INTO documento_processos VALUES(1,1,'cnj_explicito'),(2,1,'cnj_explicito'),(3,2,'cnj_explicito');''')
        candidates, eligible, codes = load(c)
        self.assertEqual(set(candidates), {1,3})
        self.assertEqual([r['cnj'] for r in eligible], ['cnj1'])
        self.assertFalse(eligible[0]['presenca_decisao'])
        self.assertEqual(codes, [6114,11946])


if __name__ == '__main__': unittest.main()
