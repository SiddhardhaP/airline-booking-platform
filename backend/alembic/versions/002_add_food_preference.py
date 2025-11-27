"""Add food_preference to bookings

Revision ID: 002_add_food_preference
Revises: 001_initial
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_food_preference'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add food_preference column to bookings table
    op.add_column('bookings', sa.Column('food_preference', sa.Boolean(), server_default='false', nullable=False))


def downgrade() -> None:
    # Remove food_preference column from bookings table
    op.drop_column('bookings', 'food_preference')

