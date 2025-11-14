"""Add arabic_segments_json column to Dua model for sync playback

Revision ID: 357d48845716
Revises: 43095058b09b
Create Date: 2025-11-11 15:02:24.036923
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '357d48845716'
down_revision: Union[str, Sequence[str], None] = '43095058b09b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('duas', sa.Column('arabic_segments_json', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('duas', 'arabic_segments_json')
