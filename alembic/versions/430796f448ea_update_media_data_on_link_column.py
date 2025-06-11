"""update media_data on link column

Revision ID: 430796f448ea
Revises: ee99eb144297
Create Date: 2025-06-11 08:39:08.309176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '430796f448ea'
down_revision: Union[str, None] = 'ee99eb144297'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE media_data
        ADD CONSTRAINT unique_link UNIQUE (link);
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE media_data
        DROP CONSTRAINT unique_link;
    """)