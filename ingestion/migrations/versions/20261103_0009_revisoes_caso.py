"""Append-only human case reviews."""
from alembic import op
from bpc_ingestion.research import RevisaoCaso

revision = "20261103_0009"
down_revision = "20261012_0008"
branch_labels = None
depends_on = None


def upgrade():
    RevisaoCaso.__table__.create(op.get_bind(), checkfirst=True)


def downgrade():
    RevisaoCaso.__table__.drop(op.get_bind(), checkfirst=True)
