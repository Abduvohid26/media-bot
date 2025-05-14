"""remove track_search_quota column from instance

Revision ID: bd84be43acc2
Revises: 3b8f747412df
Create Date: 2024-11-02 08:58:06.837603

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd84be43acc2'
down_revision: Union[str, None] = '3b8f747412df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN track_search_quota;")


def downgrade() -> None:
  pass
