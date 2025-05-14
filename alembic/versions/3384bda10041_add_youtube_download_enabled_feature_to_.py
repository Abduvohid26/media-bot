"""add youtube download enabled feature to instance table

Revision ID: 3384bda10041
Revises: 533fa446df56
Create Date: 2025-03-02 11:32:53.813299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3384bda10041'
down_revision: Union[str, None] = '533fa446df56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("ALTER TABLE INSTANCE ADD COLUMN youtube_download_feature_enabled BOOL DEFAULT FALSE;")


def downgrade() -> None:
    pass
