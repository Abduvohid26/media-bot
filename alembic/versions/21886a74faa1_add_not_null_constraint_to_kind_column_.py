"""add not null constraint to kind column in table required join

Revision ID: 21886a74faa1
Revises: 44bd78c15a54
Create Date: 2024-07-28 22:10:59.222925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '21886a74faa1'
down_revision: Union[str, None] = '44bd78c15a54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE required_join ALTER COLUMN kind SET NOT NULL;")


def downgrade() -> None:
  pass
