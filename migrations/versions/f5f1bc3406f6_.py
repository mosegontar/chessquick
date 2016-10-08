"""empty message

Revision ID: f5f1bc3406f6
Revises: e92bee2bb291
Create Date: 2016-10-08 17:04:50.853244

"""

# revision identifiers, used by Alembic.
revision = 'f5f1bc3406f6'
down_revision = 'e92bee2bb291'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'users', ['username'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    ### end Alembic commands ###
