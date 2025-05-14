"""add advertisement origin column to message table

Revision ID: 0bb13b7eed58
Revises: 5b0a6dfc720b
Create Date: 2024-05-22 17:20:25.717402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bb13b7eed58'
down_revision: Union[str, None] = '5b0a6dfc720b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE message ADD COLUMN advertisement_origin INTEGER REFERENCES advertisement (id) ON DELETE CASCADE;")


def downgrade() -> None:
  op.execute("ALTER TABLE message DROP COLUMN advertisement_origin;")
