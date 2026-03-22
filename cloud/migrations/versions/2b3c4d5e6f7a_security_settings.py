from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "2b3c4d5e6f7a"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_settings",
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
        ),
        sa.Column("ip_filter_enabled", sa.Boolean(), server_default="false"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "ip_allowlist",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cidr_block", sa.String(), nullable=False),
    )
    op.create_index(
        "ix_ip_allowlist_tenant_id",
        "ip_allowlist",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "uq_ip_allowlist_tenant_cidr",
        "ip_allowlist",
        ["tenant_id", "cidr_block"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_ip_allowlist_tenant_cidr", table_name="ip_allowlist")
    op.drop_index("ix_ip_allowlist_tenant_id", table_name="ip_allowlist")
    op.drop_table("ip_allowlist")
    op.drop_table("tenant_settings")
