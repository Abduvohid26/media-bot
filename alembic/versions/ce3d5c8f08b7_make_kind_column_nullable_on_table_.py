"""make_kind_column_nullable_on_table_advertisement

Revision ID: ce3d5c8f08b7
Revises: 1e813e2f3741
Create Date: 2025-04-09 17:25:34.779728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ce3d5c8f08b7'
down_revision: Union[str, None] = '1e813e2f3741'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE advertisement ALTER COLUMN kind DROP NOT NULL;")

def downgrade() -> None:
    pass
