"""add index to has_joined column in table required join mark

Revision ID: 3cc4f720f481
Revises: 21886a74faa1
Create Date: 2024-07-30 21:54:12.843762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cc4f720f481'
down_revision: Union[str, None] = '21886a74faa1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("CREATE INDEX index_required_join_mark_has_joined ON required_join_mark(has_joined);")


def downgrade() -> None:
  pass
