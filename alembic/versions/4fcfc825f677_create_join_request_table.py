"""create join request table

Revision ID: 4fcfc825f677
Revises: 15a525981e0a
Create Date: 2024-05-18 20:48:13.951583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fcfc825f677'
down_revision: Union[str, None] = '15a525981e0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "join_request" (
      "id" SERIAL PRIMARY KEY,
      "user_id" BIGINT NOT NULL,
      "join_request_chat_origin" INTEGER NOT NULL REFERENCES "join_request_chat" ("id") ON DELETE SET NULL,
      "instance_origin" INTEGER NOT NULL REFERENCES "instance" ("id") ON DELETE CASCADE,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  """)



def downgrade() -> None:
  op.execute("DROP TABLE join_request;")
