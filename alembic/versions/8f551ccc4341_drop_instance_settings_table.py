"""drop instance settings table

Revision ID: 8f551ccc4341
Revises: bb575590ad83
Create Date: 2024-04-16 16:29:51.789129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f551ccc4341'
down_revision: Union[str, None] = 'bb575590ad83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("DROP TABLE instance_settings")

def downgrade() -> None:
   pass
