"""Mark room responses as resolved

Revision ID: fc9664b94e6b
Revises: 395aa731622a
Create Date: 2019-04-05 12:06:35.458061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc9664b94e6b'
down_revision = '395aa731622a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('responses', sa.Column('resolved', sa. Boolean(), nullable=False, server_default='False'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('responses', 'resolved')
    # ### end Alembic commands ###
