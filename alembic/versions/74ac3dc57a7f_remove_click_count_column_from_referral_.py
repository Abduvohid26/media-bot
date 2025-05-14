"""remove click count column from referral table

Revision ID: 74ac3dc57a7f
Revises: e5976285c638
Create Date: 2024-04-22 21:53:45.495429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74ac3dc57a7f'
down_revision: Union[str, None] = 'e5976285c638'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE referral DROP COLUMN click_count")


def downgrade() -> None:
    pass
