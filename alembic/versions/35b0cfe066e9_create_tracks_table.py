"""create tracks table

Revision ID: 35b0cfe066e9
Revises: ce3d5c8f08b7
Create Date: 2025-05-27 11:23:21.739823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35b0cfe066e9'
down_revision: Union[str, None] = 'ce3d5c8f08b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("""
        CREATE TABLE tracks (
            id SERIAL PRIMARY KEY,
            query VARCHAR NOT NULL,
            video_id VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            performer VARCHAR NOT NULL,
            duration INTEGER NOT NULL,
            thumbnail_url VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

def downgrade() -> None:
    op.execute("DROP TABLE tracks;")
