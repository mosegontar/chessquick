"""empty message

Revision ID: 7086759e272f
Revises: e017ed70b3f8
Create Date: 2016-10-15 09:31:31.262126

"""

# revision identifiers, used by Alembic.
revision = '7086759e272f'
down_revision = 'e017ed70b3f8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('login_type', sa.String(length=12), nullable=True))
    op.drop_column('users', 'login_method')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('login_method', postgresql.ENUM('local', 'oauth', name='login_method'), autoincrement=False, nullable=True))
    op.drop_column('users', 'login_type')
    ### end Alembic commands ###
