"""add resume storage_path, status and is_active

Revision ID: 0003_resume_storage_and_status
Revises: 0002_add_auth_tables
Create Date: 2026-08-12 22:20:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_resume_storage_and_status'
down_revision = '0002_add_auth_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('resumes', sa.Column('storage_path', sa.String(length=1024), nullable=True))
    op.add_column('resumes', sa.Column('status', sa.String(length=32), nullable=False, server_default='UPLOADED'))
    op.add_column('resumes', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    op.drop_column('resumes', 'is_active')
    op.drop_column('resumes', 'status')
    op.drop_column('resumes', 'storage_path')
