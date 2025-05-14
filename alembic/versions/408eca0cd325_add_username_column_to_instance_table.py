"""add username column to instance table

Revision ID: 408eca0cd325
Revises: 9e136929bdd1
Create Date: 2024-06-07 11:05:33.212594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '408eca0cd325'
down_revision: Union[str, None] = '9e136929bdd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE instance ADD COLUMN username VARCHAR NOT NULL;")


def downgrade() -> None:
    pass
