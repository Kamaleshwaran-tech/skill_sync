"""add job match detail and skill gap relation

Revision ID: 20250825_0008
Revises: 0006_job_skill_types
Create Date: 2025-08-25 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250825_0008"
down_revision = "0006_job_skill_types"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "match_details",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_match_id", sa.Integer(), nullable=False),
        sa.Column("semantic_similarity", sa.Float(), nullable=True),
        sa.Column("required_skill_coverage", sa.Float(), nullable=True),
        sa.Column("preferred_skill_coverage", sa.Float(), nullable=True),
        sa.Column("experience_relevance", sa.Float(), nullable=True),
        sa.Column("project_relevance", sa.Float(), nullable=True),
        sa.Column("score_breakdown", sa.JSON(), nullable=True),
        sa.Column("strengths", sa.JSON(), nullable=True),
        sa.Column("potential_concerns", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["job_match_id"], ["job_matches.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(op.f("ix_match_details_job_match_id"), "match_details", ["job_match_id"], unique=False)



def downgrade() -> None:
    op.drop_index(op.f("ix_match_details_job_match_id"), table_name="match_details")
    op.drop_table("match_details")
