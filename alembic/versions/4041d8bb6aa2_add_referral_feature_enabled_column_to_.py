"""add referral_feature_enabled column to instance table

Revision ID: 4041d8bb6aa2
Revises: 5b983a323a26
Create Date: 2024-12-19 18:39:04.176595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4041d8bb6aa2'
down_revision: Union[str, None] = '5b983a323a26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN referral_feature_enabled BOOL DEFAULT FALSE")


def downgrade() -> None:
    pass
