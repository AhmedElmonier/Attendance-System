"""governance tables and indices

Revision ID: 1a2b3c4d5e6f
Revises: previous_revision_id
Create Date: 2026-03-22 19:40:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    # Creating approval_requests
    op.create_table(
        'approval_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('change_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('maker_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('checker_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(), server_default='PENDING', nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    op.create_index(op.f('ix_approval_requests_tenant_id'), 'approval_requests', ['tenant_id'], unique=False)

    # Creating audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('actor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('old_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    # T027 [P] Create PostgreSQL index on (tenant_id, timestamp) for audit log performance (SC-002)
    op.create_index('ix_audit_logs_tenant_timestamp', 'audit_logs', ['tenant_id', 'timestamp'], unique=False)

def downgrade() -> None:
    op.drop_index('ix_audit_logs_tenant_timestamp', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_approval_requests_tenant_id'), table_name='approval_requests')
    op.drop_table('approval_requests')
