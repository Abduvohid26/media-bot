"""remove language origin column from required join table

Revision ID: 1892358e2ad4
Revises: 4c2ff3256c7d
Create Date: 2024-04-28 19:53:42.044733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1892358e2ad4'
down_revision: Union[str, None] = '4c2ff3256c7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE required_join DROP COLUMN language_origin")


def downgrade() -> None:
  pass
