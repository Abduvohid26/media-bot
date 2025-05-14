"""change type of kind column in table required join

Revision ID: 44bd78c15a54
Revises: 399ee62f8d4b
Create Date: 2024-07-28 21:16:41.658326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44bd78c15a54'
down_revision: Union[str, None] = '399ee62f8d4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE required_join DROP COLUMN kind;")
  op.execute("CREATE TYPE enum_required_join_kind AS ENUM ('MEDIA_QUERY', 'MEDIA_DOWNLOAD');")
  op.execute("ALTER TABLE required_join ADD COLUMN kind enum_required_join_kind DEFAULT 'MEDIA_QUERY';")


def downgrade() -> None:
    pass
