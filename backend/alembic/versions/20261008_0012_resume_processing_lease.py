"""Recover interrupted parsing without letting stale workers overwrite newer results."""

from alembic import op
import sqlalchemy as sa

revision = "20261008_0012"
down_revision = "20261008_0011"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "resumes", sa.Column("processing_started_at", sa.DateTime(), nullable=True)
    )


def downgrade():
    with op.batch_alter_table("resumes") as batch:
        batch.drop_column("processing_started_at")
