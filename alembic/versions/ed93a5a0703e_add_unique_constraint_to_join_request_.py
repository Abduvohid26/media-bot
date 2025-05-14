"""add unique constraint to join request table

Revision ID: ed93a5a0703e
Revises: 89ccc581f294
Create Date: 2024-07-23 10:03:02.752120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed93a5a0703e'
down_revision: Union[str, None] = '89ccc581f294'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE join_request ADD CONSTRAINT join_request_unique_constraint UNIQUE (user_id, join_request_chat_origin, instance_origin);")


def downgrade() -> None:
  pass
