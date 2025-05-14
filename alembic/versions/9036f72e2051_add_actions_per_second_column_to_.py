"""add actions per second column to instance

Revision ID: 9036f72e2051
Revises: a086e4e85ad4
Create Date: 2024-07-26 18:20:44.603651

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9036f72e2051'
down_revision: Union[str, None] = 'a086e4e85ad4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN actions_per_second INTEGER DEFAULT -1;")


def downgrade() -> None:
  pass
