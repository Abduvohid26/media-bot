"""remove track_download_quota column from instance

Revision ID: d83f8b6ab9af
Revises: bd84be43acc2
Create Date: 2024-11-02 08:58:36.509245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd83f8b6ab9af'
down_revision: Union[str, None] = 'bd84be43acc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN track_download_quota;")


def downgrade() -> None:
  pass
