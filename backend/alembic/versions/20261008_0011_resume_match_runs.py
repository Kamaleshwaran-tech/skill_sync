"""Add resume-specific search snapshots. Preserve all existing tables/data."""

from alembic import op
import sqlalchemy as sa

revision = "20261008_0011"
down_revision = "20260911_0010"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "resume_match_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "resume_id",
            sa.Integer(),
            sa.ForeignKey("resumes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "analysis_id",
            sa.Integer(),
            sa.ForeignKey("resume_analyses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("result", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_resume_match_runs_user_id", "resume_match_runs", ["user_id"])
    op.create_index(
        "ix_resume_match_runs_resume_id", "resume_match_runs", ["resume_id"]
    )


def downgrade():
    op.drop_table("resume_match_runs")
