"""change type of column group id in table group

Revision ID: f5e45ba9de5f
Revises: 13a7882728e3
Create Date: 2024-07-27 21:11:34.231362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5e45ba9de5f'
down_revision: Union[str, None] = '13a7882728e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute('ALTER TABLE "group" ALTER COLUMN group_id TYPE BIGINT;')


def downgrade() -> None:
    pass
