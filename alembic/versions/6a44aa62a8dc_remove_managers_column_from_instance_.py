"""remove managers column from instance table

Revision ID: 6a44aa62a8dc
Revises: 0f20042e7536
Create Date: 2024-05-29 22:23:57.117652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a44aa62a8dc'
down_revision: Union[str, None] = '0f20042e7536'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance DROP COLUMN managers;")


def downgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN managers JSONB;")