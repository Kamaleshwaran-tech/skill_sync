"""add job skill type classification

Revision ID: 0006_job_skill_types
Revises: 0005_job_ingestion_tracking
Create Date: 2026-08-25 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0006_job_skill_types'
down_revision = '0005_job_ingestion_tracking'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('job_skills', schema=None) as batch_op:
        batch_op.add_column(sa.Column('skill_type', sa.String(length=32), nullable=False, server_default='required'))


def downgrade():
    with op.batch_alter_table('job_skills', schema=None) as batch_op:
        batch_op.drop_column('skill_type')
