"""create wallets table

Revision ID: 001
Revises:
Create Date: 2026-05-17 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'wallets',
        sa.Column('uuid', UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column('balance', sa.Numeric(10, 2), server_default='100.00', nullable=False),
    )

def downgrade() -> None:
    op.drop_table('wallets')