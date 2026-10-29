import io
import unittest
import uuid
from pathlib import Path

from openpyxl import Workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from bpc_ingestion.database import make_engine
from bpc_ingestion.inss_benefits import InssBenefitsClient, aggregate_rows, aggregate_xlsx, store_aggregates
from bpc_ingestion.models import Base, Coleta, IndicadorInssIndeferimento


class InssBenefitsTest(unittest.TestCase):
    def test_cli_single_and_multiple_states_mutually_exclusive(self):
        from bpc_ingestion.cli import construir_parser
        parser = construir_parser()
        args = parser.parse_args(['inss-indeferimentos', '--competencia', '202601', '--ufs', 'DF', 'GO', 'MG'])
        self.assertEqual(args.ufs, ['DF', 'GO', 'MG'])
        self.assertIsNone(args.uf)
        single = parser.parse_args(['inss-concessoes', '--competencia', '202601', '--uf', 'DF'])
        self.assertEqual(single.uf, 'DF')
        self.assertIsNone(single.ufs)
        with self.assertRaises(SystemExit):
            parser.parse_args(['inss-concessoes', '--competencia', '202601', '--uf', 'DF', '--ufs', 'GO'])

    def test_multi_state_equals_single_unions_and_rejects_invalid(self):
        from collections import Counter
        multi, quality = aggregate_rows(self.rows(), ['DF', 'SP', 'DF'], 202608)
        expected = Counter()
        for state in ('DF', 'SP'):
            expected.update(aggregate_rows(self.rows(), state, 202608)[0])
        self.assertEqual(multi, expected)
        self.assertEqual(quality['selecionadas_por_uf'], {'DF': 3, 'SP': 1})
        for states in ([], ['DF', 'ZZ'], [True]):
            with self.assertRaises(ValueError):
                aggregate_rows(self.rows(), states, 202608)
        with self.assertRaises(ValueError):
            aggregate_rows(iter([['Competência indeferimento', 'Espécie', 'Motivo', 'UF'],
                                 [202607, 31, 'Outro', 'SP']]), ['DF', 'GO'], 202608)

    def rows(self):
        return iter([
            ["INDEFERIDOS DADOS ABERTOS AGOSTO 2026"],
            ["Competência indeferimento", "Espécie", "Espécie", "Motivo Indeferimento", "UF"],
            [202608, 87, "Pessoa com Deficiência", "Renda", "Distrito Federal"],
            [202608, 87, "Pessoa com Deficiência", "Renda", "DF"],
            [202608, 88, "Idoso", None, "DF"],
            [202608, 31, "Outro", "Perícia", "DF"],
            [202608, 88, "Idoso", "Renda", "SP"],
        ])

    def test_real_header_duplicate_species_title_and_counts(self):
        counts, quality = aggregate_rows(self.rows(), "DF", 202608)
        self.assertEqual(counts[("DF", 87, "Renda")], 2)
        self.assertEqual(counts[("DF", 88, "Não informado")], 1)
        self.assertEqual(quality["linhas_lidas"], 5)
        self.assertEqual(quality["linhas_selecionadas"], 3)
        self.assertEqual(quality["linha_cabecalho"], 2)

    def test_rejects_missing_column_invalid_code_or_month(self):
        with self.assertRaises(ValueError):
            aggregate_rows(iter([["Foo"], ["Bar"]]), "DF", 202608)
        for row in ([202607, 87, "Renda", "DF"], [202608, "BPC idoso", "Renda", "DF"]):
            with self.subTest(row=row), self.assertRaises(ValueError):
                aggregate_rows(iter([["Competência indeferimento", "Espécie", "Motivo", "UF"], row]), "DF", 202608)

    def test_xlsx_streaming_and_unknown_uf_not_selected(self):
        workbook = Workbook()
        for row in self.rows():
            workbook.active.append(row)
        output = io.BytesIO()
        workbook.save(output)
        counts, quality = aggregate_xlsx(output.getvalue(), "DF", 202608)
        self.assertEqual(sum(counts.values()), 3)
        with self.assertRaises(ValueError):
            aggregate_xlsx(output.getvalue(), "ZZ", 202608)
        counts, quality = aggregate_rows(iter([["Espécie", "Motivo", "UF"], [87, "Renda", "??"]]), "DF")
        self.assertEqual(quality["bpc_uf_desconhecida"], 1)
        self.assertEqual(sum(counts.values()), 0)

    def test_resource_requires_unique_explicit_month(self):
        client = InssBenefitsClient()
        package = {"resources": [{"id": "1", "format": "XLSX", "name": "Benefícios Indeferidos Agosto 2026"}]}
        self.assertEqual(client.monthly_resource(package, 202608)["id"], "1")
        for period in (202699, 202607):
            with self.assertRaises(ValueError):
                client.monthly_resource(package, period)
        package["resources"].append(dict(package["resources"][0], id="2"))
        with self.assertRaises(ValueError):
            client.monthly_resource(package, 202608)

    def test_aggregate_versions_no_personal_rows_no_duplicate(self):
        engine = make_engine("sqlite://")
        Base.metadata.create_all(engine)
        run = str(uuid.uuid4())
        resource = {"id": "1", "url": "https://example.test/202608.xlsx"}
        counts, _ = aggregate_rows(self.rows(), "DF", 202608)
        try:
            with Session(engine) as session, session.begin():
                session.add(Coleta(id=uuid.UUID(run), fonte="inss_indeferimentos"))
                session.flush()
                self.assertEqual(store_aggregates(session, counts, resource, 202608, b"xlsx bytes", Path("raw.gz"), run), 2)
                session.flush()
                self.assertEqual(store_aggregates(session, counts, resource, 202608, b"xlsx bytes", Path("raw.gz"), run), 0)
                self.assertEqual(store_aggregates(session, counts, resource, 202608, b"updated bytes", Path("new.gz"), run), 2)
            with Session(engine) as session:
                self.assertEqual(len(list(session.scalars(select(IndicadorInssIndeferimento)))), 4)
        finally:
            engine.dispose()
