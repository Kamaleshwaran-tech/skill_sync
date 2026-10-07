"""repair access-token revocation table when an earlier migration was partial"""

from alembic import op
import sqlalchemy as sa


revision = "20260911_0010"
down_revision = "20260907_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()
    sa.Table("users", metadata, sa.Column("id", sa.Integer(), primary_key=True))
    preferences = sa.Table(
        "user_preferences",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("preferences", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    preferences.create(bind=bind, checkfirst=True)
    table = sa.Table(
        "revoked_access_tokens",
        metadata,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jti", sa.String(length=128), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    table.create(bind=bind, checkfirst=True)
    sa.Index("ix_revoked_access_tokens_user_id", table.c.user_id).create(bind=bind, checkfirst=True)
    sa.Index("ix_revoked_access_tokens_jti", table.c.jti).create(bind=bind, checkfirst=True)


def downgrade() -> None:
    bind = op.get_bind()
    metadata = sa.MetaData()
    table = sa.Table("revoked_access_tokens", metadata, autoload_with=bind)
    table.drop(bind=bind, checkfirst=True)
    preferences = sa.Table("user_preferences", metadata, autoload_with=bind)
    preferences.drop(bind=bind, checkfirst=True)
