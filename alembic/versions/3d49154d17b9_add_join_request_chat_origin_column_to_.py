"""add join request chat origin column to message table

Revision ID: 3d49154d17b9
Revises: 4fcfc825f677
Create Date: 2024-05-19 15:19:32.874265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d49154d17b9'
down_revision: Union[str, None] = '4fcfc825f677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE message ADD COLUMN join_request_chat_origin INTEGER REFERENCES join_request_chat (id) ON DELETE CASCADE;")


def downgrade() -> None:
  op.execute("ALTER TABLE message DROP COLUMN join_request_chat_origin;")
