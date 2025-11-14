"""Add DuaShareLink table for short URLs

Revision ID: 806db245e78c
Revises: 6094201b6bfe
Create Date: 2025-11-14 13:32:19.111330
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '806db245e78c'
down_revision: Union[str, Sequence[str], None] = '6094201b6bfe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Drop tables in dependency order: dependents first
    op.drop_table('ratings')
    op.drop_index(op.f('ix_zakat_records_id'), table_name='zakat_records')
    op.drop_index(op.f('ix_zakat_records_user_id'), table_name='zakat_records')
    op.drop_table('zakat_records')
    
    op.drop_table('admin_notes')
    
    op.drop_table('files')          # files depends on messages
    op.drop_table('messages')       # messages depends on conversations
    
    op.drop_table('conversations')
    op.drop_table('admin_users')
    
    op.drop_index(op.f('ix_contact_messages_id'), table_name='contact_messages')
    op.drop_table('contact_messages')


def downgrade() -> None:
    """Downgrade schema."""

    op.create_table(
        'contact_messages',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(length=100), nullable=False),
        sa.Column('email', sa.VARCHAR(length=100), nullable=False),
        sa.Column('subject', sa.VARCHAR(length=150), nullable=False),
        sa.Column('message', sa.TEXT(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('contact_messages_pkey'))
    )
    op.create_index(op.f('ix_contact_messages_id'), 'contact_messages', ['id'], unique=False)

    op.create_table(
        'admin_users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.VARCHAR(length=255), nullable=False),
        sa.Column('email', sa.VARCHAR(length=255), nullable=False),
        sa.Column('password_hash', sa.VARCHAR(length=255), nullable=False),
        sa.Column('is_online', sa.BOOLEAN(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id', name='admin_users_pkey'),
        sa.UniqueConstraint('email', name='admin_users_email_key')
    )

    op.create_table(
        'conversations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.VARCHAR(length=20), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='conversations_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='conversations_pkey')
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('sender_type', sa.VARCHAR(length=10), nullable=False),
        sa.Column('sender_id', sa.UUID(), nullable=True),
        sa.Column('message_text', sa.TEXT(), nullable=True),
        sa.Column('message_type', sa.VARCHAR(length=20), nullable=True),
        sa.Column('file_url', sa.VARCHAR(), nullable=True),
        sa.Column('status', sa.VARCHAR(length=20), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name=op.f('messages_conversation_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('messages_pkey'))
    )

    op.create_table(
        'files',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('message_id', sa.UUID(), nullable=True),
        sa.Column('file_name', sa.VARCHAR(length=255), nullable=True),
        sa.Column('file_type', sa.VARCHAR(length=50), nullable=True),
        sa.Column('file_size', sa.BIGINT(), nullable=True),
        sa.Column('file_url', sa.VARCHAR(), nullable=True),
        sa.Column('uploaded_at', postgresql.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], name=op.f('files_message_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('files_pkey'))
    )

    op.create_table(
        'admin_notes',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('admin_id', sa.UUID(), nullable=False),
        sa.Column('note_text', sa.TEXT(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], name=op.f('admin_notes_admin_id_fkey')),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name=op.f('admin_notes_conversation_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('admin_notes_pkey'))
    )

    op.create_table(
        'zakat_records',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), nullable=True),
        sa.Column('name', sa.VARCHAR(), nullable=True),
        sa.Column('assets_total', sa.DOUBLE_PRECISION(precision=53), nullable=False),
        sa.Column('savings', sa.DOUBLE_PRECISION(precision=53), nullable=False),
        sa.Column('gold_price_per_gram', sa.DOUBLE_PRECISION(precision=53), nullable=True),
        sa.Column('nisab', sa.DOUBLE_PRECISION(precision=53), nullable=True),
        sa.Column('zakat_amount', sa.DOUBLE_PRECISION(precision=53), nullable=False),
        sa.Column('type', sa.VARCHAR(), nullable=False),
        sa.Column('note', sa.TEXT(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('zakat_records_pkey'))
    )
    op.create_index(op.f('ix_zakat_records_user_id'), 'zakat_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_zakat_records_id'), 'zakat_records', ['id'], unique=False)

    op.create_table(
        'ratings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('conversation_id', sa.UUID(), nullable=False),
        sa.Column('rating', sa.INTEGER(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], name=op.f('ratings_conversation_id_fkey')),
        sa.PrimaryKeyConstraint('id', name=op.f('ratings_pkey'))
    )
