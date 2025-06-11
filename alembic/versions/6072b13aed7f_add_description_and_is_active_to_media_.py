"""add description and is_active to media_data

Revision ID: 6072b13aed7f
Revises: 698c34858f55
Create Date: 2025-06-10 09:16:57.199655

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6072b13aed7f'
down_revision: Union[str, None] = '698c34858f55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('media_data', sa.Column('bot_token', sa.String(255), nullable=True))
    op.add_column('media_data', sa.Column('bot_username', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('media_data', 'bot_token')
    op.drop_column('media_data', 'bot_username')