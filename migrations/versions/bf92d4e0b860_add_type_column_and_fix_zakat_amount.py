"""Add type column and fix zakat_amount

Revision ID: bf92d4e0b860
Revises: f82e3d91c545
Create Date: 2025-10-16 13:27:04.858899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf92d4e0b860'
down_revision: Union[str, Sequence[str], None] = 'f82e3d91c545'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Add 'type' column with default 'cash' for existing rows
    op.add_column(
        'zakat_records',
        sa.Column('type', sa.String(), nullable=False, server_default='cash')
    )
    # Make sure zakat_amount is not nullable and has default
    op.alter_column(
        'zakat_records',
        'zakat_amount',
        existing_type=sa.Float(),
        nullable=False,
        server_default='0'
    )

def downgrade():
    op.drop_column('zakat_records', 'type')

