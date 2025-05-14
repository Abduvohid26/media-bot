"""set default value 0 for required join mark view count

Revision ID: cc5b114ddb23
Revises: 0bb13b7eed58
Create Date: 2024-05-26 17:58:32.073057

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc5b114ddb23'
down_revision: Union[str, None] = '0bb13b7eed58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE ONLY required_join_mark ALTER COLUMN view_count SET DEFAULT 0;")


def downgrade() -> None:
  op.execute("ALTER TABLE ONLY required_join_mark ALTER COLUMN view_count SET DEFAULT 1;")
