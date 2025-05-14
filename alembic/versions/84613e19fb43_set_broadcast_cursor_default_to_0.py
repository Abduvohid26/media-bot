"""set broadcast cursor default to 0

Revision ID: 84613e19fb43
Revises: e7c0f84e69af
Create Date: 2024-10-27 10:00:39.764642

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84613e19fb43'
down_revision: Union[str, None] = 'e7c0f84e69af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("DROP TRIGGER IF EXISTS broadcast_set_is_running_false_if_cursor_exceeds_jobs_trigger ON broadcast;")
  op.execute("ALTER TABLE broadcast ALTER COLUMN cursor TYPE BIGINT;")


def downgrade() -> None:
  pass
