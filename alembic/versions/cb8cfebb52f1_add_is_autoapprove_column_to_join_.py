"""add is autoapprove column to join request chat table

Revision ID: cb8cfebb52f1
Revises: 7bcf70289d3d
Create Date: 2024-07-23 08:17:05.098074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb8cfebb52f1'
down_revision: Union[str, None] = '7bcf70289d3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE join_request_chat ADD COLUMN is_autoapprove BOOL DEFAULT FALSE;")


def downgrade() -> None:
  pass
