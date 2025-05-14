"""add referral origin to account table

Revision ID: 1600598b9d9b
Revises: 1702a65311ce
Create Date: 2024-04-21 12:06:29.280491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1600598b9d9b'
down_revision: Union[str, None] = '1702a65311ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE account ADD COLUMN referral_origin INTEGER REFERENCES referral (id) ON DELETE SET NULL")


def downgrade() -> None:
  op.execute("ALTER TABLE account DROP COLUMN referral_origin")
