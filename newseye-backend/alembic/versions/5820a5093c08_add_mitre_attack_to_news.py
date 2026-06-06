"""Add mitre_attack to News

Revision ID: 5820a5093c08
Revises: d40057a72b9d
Create Date: 2026-06-06 14:04:20.589080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5820a5093c08'
down_revision: Union[str, Sequence[str], None] = 'd40057a72b9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('news', sa.Column('mitre_attack', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('news', 'mitre_attack')
