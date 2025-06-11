"""link and file type change text

Revision ID: ee99eb144297
Revises: 6072b13aed7f
Create Date: 2025-06-10 11:15:35.494811

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee99eb144297'
down_revision: Union[str, None] = '6072b13aed7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # file_id ni VARCHAR(255) dan TEXT ga o'zgartirish
    op.alter_column('media_data', 'file_id',
                   existing_type=sa.VARCHAR(255),
                   type_=sa.Text(),
                   nullable=False)
    
    # link ni VARCHAR(255) dan TEXT ga o'zgartirish
    op.alter_column('media_data', 'link',
                   existing_type=sa.VARCHAR(255),
                   type_=sa.Text(),
                   nullable=False)


def downgrade() -> None:
    # file_id ni TEXT dan VARCHAR(255) ga qaytarish
    op.alter_column('media_data', 'file_id',
                   existing_type=sa.Text(),
                   type_=sa.VARCHAR(255),
                   nullable=False)
    
    # link ni TEXT dan VARCHAR(255) ga qaytarish
    op.alter_column('media_data', 'link',
                   existing_type=sa.Text(),
                   type_=sa.VARCHAR(255),
                   nullable=False)