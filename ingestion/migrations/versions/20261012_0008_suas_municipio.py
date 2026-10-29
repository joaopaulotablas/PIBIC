"""Indicadores municipais agregados do Censo SUAS."""
from alembic import op

from bpc_ingestion.models import IndicadorSuasMunicipio


revision = "20261012_0008"
down_revision = "20261006_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    IndicadorSuasMunicipio.__table__.create(bind=op.get_bind(), checkfirst=True)


def downgrade() -> None:
    IndicadorSuasMunicipio.__table__.drop(bind=op.get_bind(), checkfirst=True)
