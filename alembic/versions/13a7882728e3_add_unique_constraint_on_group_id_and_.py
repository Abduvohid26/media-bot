"""add unique constraint on group id and instance id in table group

Revision ID: 13a7882728e3
Revises: 451d2236aa48
Create Date: 2024-07-27 21:02:47.666847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13a7882728e3'
down_revision: Union[str, None] = '451d2236aa48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute('ALTER TABLE "group" ADD UNIQUE (group_id, instance_origin);')


def downgrade() -> None:
    pass
