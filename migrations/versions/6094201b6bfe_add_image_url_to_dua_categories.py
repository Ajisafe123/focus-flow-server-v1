"""Add image_url to dua_categories

Revision ID: 6094201b6bfe
Revises: c3b91166a2db
Create Date: 2025-11-13 09:59:00.797654
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6094201b6bfe'
down_revision: Union[str, Sequence[str], None] = 'c3b91166a2db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ✅ Only add the new column; don't drop any tables
    op.add_column('dua_categories', sa.Column('image_url', sa.String(length=512), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # ✅ Only remove the new column
    op.drop_column('dua_categories', 'image_url')
