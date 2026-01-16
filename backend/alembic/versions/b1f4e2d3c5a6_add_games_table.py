"""Add games table

Revision ID: b1f4e2d3c5a6
Revises: aaecd3683a34
Create Date: 2024-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1f4e2d3c5a6'
down_revision: Union[str, None] = 'aaecd3683a34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create games table
    op.create_table(
        'games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('igdb_id', sa.Integer(), nullable=True),
        sa.Column('rawg_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('storyline', sa.Text(), nullable=True),
        sa.Column('cover_url', sa.String(length=512), nullable=True),
        sa.Column('screenshots', sa.JSON(), nullable=True),
        sa.Column('artworks', sa.JSON(), nullable=True),
        sa.Column('videos', sa.JSON(), nullable=True),
        sa.Column('release_date', sa.DateTime(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('rating_count', sa.Integer(), nullable=True),
        sa.Column('metacritic_score', sa.Integer(), nullable=True),
        sa.Column('platforms', sa.JSON(), nullable=True),
        sa.Column('genres', sa.JSON(), nullable=True),
        sa.Column('themes', sa.JSON(), nullable=True),
        sa.Column('game_modes', sa.JSON(), nullable=True),
        sa.Column('developers', sa.JSON(), nullable=True),
        sa.Column('publishers', sa.JSON(), nullable=True),
        sa.Column('websites', sa.JSON(), nullable=True),
        sa.Column('similar_games', sa.JSON(), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_games_id'), 'games', ['id'], unique=False)
    op.create_index(op.f('ix_games_igdb_id'), 'games', ['igdb_id'], unique=True)
    op.create_index(op.f('ix_games_rawg_id'), 'games', ['rawg_id'], unique=True)
    op.create_index(op.f('ix_games_name'), 'games', ['name'], unique=False)
    op.create_index(op.f('ix_games_slug'), 'games', ['slug'], unique=True)
    op.create_index(op.f('ix_games_release_date'), 'games', ['release_date'], unique=False)
    op.create_index(op.f('ix_games_last_synced_at'), 'games', ['last_synced_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_games_last_synced_at'), table_name='games')
    op.drop_index(op.f('ix_games_release_date'), table_name='games')
    op.drop_index(op.f('ix_games_slug'), table_name='games')
    op.drop_index(op.f('ix_games_name'), table_name='games')
    op.drop_index(op.f('ix_games_rawg_id'), table_name='games')
    op.drop_index(op.f('ix_games_igdb_id'), table_name='games')
    op.drop_index(op.f('ix_games_id'), table_name='games')
    
    # Drop table
    op.drop_table('games')
