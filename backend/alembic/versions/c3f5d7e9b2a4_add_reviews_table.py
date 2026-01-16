"""Add reviews table

Revision ID: c3f5d7e9b2a4
Revises: b1f4e2d3c5a6
Create Date: 2026-01-14 21:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f5d7e9b2a4'
down_revision: Union[str, None] = 'b1f4e2d3c5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('rating', sa.Float(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('playtime_hours', sa.Integer(), nullable=True),
        sa.Column('platform', sa.String(length=100), nullable=True),
        sa.Column('is_recommended', sa.Boolean(), nullable=False),
        sa.Column('helpful_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    op.create_index(op.f('ix_reviews_user_id'), 'reviews', ['user_id'], unique=False)
    op.create_index(op.f('ix_reviews_game_id'), 'reviews', ['game_id'], unique=False)
    
    # Create unique constraint for one review per user per game
    op.create_index('ix_reviews_user_game_unique', 'reviews', ['user_id', 'game_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_reviews_user_game_unique', table_name='reviews')
    op.drop_index(op.f('ix_reviews_game_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_user_id'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_id'), table_name='reviews')
    
    # Drop table
    op.drop_table('reviews')
