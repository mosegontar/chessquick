"""empty message

Revision ID: 9ebace1bda8c
Revises: 9bc711091150
Create Date: 2016-10-06 18:05:16.489448

"""

# revision identifiers, used by Alembic.
revision = '9ebace1bda8c'
down_revision = '9bc711091150'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.String(length=64), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'username')
    ### end Alembic commands ###
