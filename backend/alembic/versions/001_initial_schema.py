"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create cached_offers table
    op.create_table(
        'cached_offers',
        sa.Column('offer_id', sa.String(), nullable=False),
        sa.Column('origin', sa.String(), nullable=False),
        sa.Column('destination', sa.String(), nullable=False),
        sa.Column('depart_ts', sa.DateTime(), nullable=False),
        sa.Column('arrive_ts', sa.DateTime(), nullable=False),
        sa.Column('airline', sa.String(), nullable=False),
        sa.Column('flight_no', sa.String(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), server_default='INR'),
        sa.Column('seats', sa.Integer(), server_default='1'),
        sa.Column('payload', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('cached_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('expire_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('offer_id')
    )
    op.create_index(op.f('ix_cached_offers_offer_id'), 'cached_offers', ['offer_id'], unique=False)
    op.create_index(op.f('ix_cached_offers_origin'), 'cached_offers', ['origin'], unique=False)
    op.create_index(op.f('ix_cached_offers_destination'), 'cached_offers', ['destination'], unique=False)
    
    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('booking_id', sa.String(), nullable=False),
        sa.Column('user_email', sa.String(), nullable=False),
        sa.Column('offer_id', sa.String(), nullable=False),
        sa.Column('passengers', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), server_default='INR'),
        sa.Column('payment_status', sa.String(), server_default='pending'),
        sa.Column('status', sa.String(), server_default='confirmed'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['offer_id'], ['cached_offers.offer_id'], ),
        sa.PrimaryKeyConstraint('booking_id')
    )
    op.create_index(op.f('ix_bookings_booking_id'), 'bookings', ['booking_id'], unique=False)
    op.create_index(op.f('ix_bookings_user_email'), 'bookings', ['user_email'], unique=False)
    
    # Create convo_memory table
    op.create_table(
        'convo_memory',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_email', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_convo_memory_id'), 'convo_memory', ['id'], unique=False)
    op.create_index(op.f('ix_convo_memory_user_email'), 'convo_memory', ['user_email'], unique=False)
    op.create_index(op.f('ix_convo_memory_created_at'), 'convo_memory', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_convo_memory_created_at'), table_name='convo_memory')
    op.drop_index(op.f('ix_convo_memory_user_email'), table_name='convo_memory')
    op.drop_index(op.f('ix_convo_memory_id'), table_name='convo_memory')
    op.drop_table('convo_memory')
    
    op.drop_index(op.f('ix_bookings_user_email'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_booking_id'), table_name='bookings')
    op.drop_table('bookings')
    
    op.drop_index(op.f('ix_cached_offers_destination'), table_name='cached_offers')
    op.drop_index(op.f('ix_cached_offers_origin'), table_name='cached_offers')
    op.drop_index(op.f('ix_cached_offers_offer_id'), table_name='cached_offers')
    op.drop_table('cached_offers')

