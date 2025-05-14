"""add is auto decline column to join request chat table

Revision ID: a086e4e85ad4
Revises: ed93a5a0703e
Create Date: 2024-07-23 10:26:47.700704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a086e4e85ad4'
down_revision: Union[str, None] = 'ed93a5a0703e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE join_request_chat ADD COLUMN is_autodecline BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
