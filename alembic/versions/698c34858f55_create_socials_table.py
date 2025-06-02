"""create socials table

Revision ID: 698c34858f55
Revises: 35b0cfe066e9
Create Date: 2025-05-31 04:43:34.886431

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '698c34858f55'
down_revision: Union[str, None] = '35b0cfe066e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE media_data (
            id SERIAL PRIMARY KEY,
            platform VARCHAR(50) NOT NULL,
            link VARCHAR(255) NOT NULL,
            file_id VARCHAR(255) NOT NULL,
            caption TEXT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE media_data;")