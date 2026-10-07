"""add resume analyses table

Revision ID: 0004_resume_analyses
Revises: 0003_resume_storage_and_status
Create Date: 2026-08-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_resume_analyses'
down_revision = '0003_resume_storage_and_status'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'resume_analyses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('resume_id', sa.Integer(), sa.ForeignKey('resumes.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('profile', sa.JSON(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )


def downgrade():
    op.drop_table('resume_analyses')
