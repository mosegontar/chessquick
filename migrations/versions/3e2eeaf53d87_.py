"""empty message

Revision ID: 3e2eeaf53d87
Revises: None
Create Date: 2016-10-08 21:24:30.862944

"""

# revision identifiers, used by Alembic.
revision = '3e2eeaf53d87'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('_password', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('login_method', sa.Enum('local', 'oauth', name='login_method'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('match_url', sa.String(length=8), nullable=True),
    sa.Column('white_player_id', sa.Integer(), nullable=True),
    sa.Column('black_player_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['black_player_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['white_player_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('match_url')
    )
    op.create_table('rounds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('turn_number', sa.Integer(), nullable=True),
    sa.Column('date_of_turn', sa.DateTime(), nullable=True),
    sa.Column('fen_string', sa.String(length=80), nullable=True),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rounds')
    op.drop_table('matches')
    op.drop_table('users')
    ### end Alembic commands ###
