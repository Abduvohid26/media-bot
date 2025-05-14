"""set default value for click_count in referral table

Revision ID: 906f8dcce9ca
Revises: a8bfe76bd0fa
Create Date: 2024-04-21 12:37:03.049269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '906f8dcce9ca'
down_revision: Union[str, None] = 'a8bfe76bd0fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE referral ALTER COLUMN click_count SET DEFAULT 0")


def downgrade() -> None:
  op.execute("ALTER TABLE referral ALTER COLUMN click_count DROP DEFAULT")
