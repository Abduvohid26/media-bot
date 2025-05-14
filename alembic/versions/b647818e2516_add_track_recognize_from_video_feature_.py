"""add_track_recognize_from_video_feature_enabled_column_to_instance_table

Revision ID: b647818e2516
Revises: 3384bda10041
Create Date: 2025-03-10 11:16:06.334924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b647818e2516'
down_revision: Union[str, None] = '3384bda10041'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
