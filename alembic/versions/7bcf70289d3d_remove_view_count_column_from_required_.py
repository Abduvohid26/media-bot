"""remove view count column from required join mark table

Revision ID: 7bcf70289d3d
Revises: 47ef8b9705e7
Create Date: 2024-07-21 11:58:06.727008

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7bcf70289d3d'
down_revision: Union[str, None] = '47ef8b9705e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE required_join_mark DROP COLUMN view_count;")


def downgrade() -> None:
    pass
