"""create broadcast set is running false when cursor exceeds jobs trigger

Revision ID: 72dc3bb48fb5
Revises: 52cfade021f0
Create Date: 2024-06-08 10:55:50.887437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72dc3bb48fb5'
down_revision: Union[str, None] = '52cfade021f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE OR REPLACE FUNCTION broadcast_set_is_running_false_if_cursor_exceeds_jobs_function()
    RETURNS trigger
    LANGUAGE plpgsql AS
    $func$
    BEGIN
      IF NEW.cursor >= NEW.jobs THEN
        UPDATE "broadcast" SET "is_running" = FALSE WHERE "id" = NEW.id;
      END IF;
    RETURN NEW;
    END
    $func$;


    CREATE OR REPLACE TRIGGER broadcast_set_is_running_false_if_cursor_exceeds_jobs_trigger
    AFTER UPDATE OF cursor ON broadcast
    FOR EACH ROW EXECUTE PROCEDURE broadcast_set_is_running_false_if_cursor_exceeds_jobs_function();
  """)


def downgrade() -> None:
  pass
