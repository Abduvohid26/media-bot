"""add_track_search_used_to_instance_table

Revision ID: 74c57110e19e
Revises: 81f4fd8ddd69
Create Date: 2024-09-04 17:00:55.201030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74c57110e19e'
down_revision: Union[str, None] = '81f4fd8ddd69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN track_search_used INTEGER DEFAULT 0;")


def downgrade() -> None:
    pass
