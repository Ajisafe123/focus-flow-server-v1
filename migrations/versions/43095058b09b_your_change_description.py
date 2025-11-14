"""your change description

Revision ID: 43095058b09b
Revises: 69d3bfe217ba
Create Date: 2025-11-11 01:31:53.501673
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '43095058b09b'
down_revision: Union[str, Sequence[str], None] = '69d3bfe217ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema without dropping any existing tables."""
    # Only safe operations
    op.create_index(op.f('ix_dua_categories_id'), 'dua_categories', ['id'], unique=False)
    # Add any other non-destructive schema changes here
    # Do NOT drop any tables to preserve data


def downgrade() -> None:
    """Downgrade schema safely."""
    # Remove indexes created in upgrade
    op.drop_index(op.f('ix_dua_categories_id'), table_name='dua_categories')
    # Recreate previous index if necessary
    op.create_index(op.f('ix_categories_id'), 'dua_categories', ['id'], unique=False)
