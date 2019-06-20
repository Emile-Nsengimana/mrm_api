"""add admin notifications table

Revision ID: f0873fb8edb3
Revises: af8e4f84b552
Create Date: 2019-06-27 13:31:19.694650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0873fb8edb3'
down_revision = 'af8e4f84b552'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DROP TYPE statustype;')
    op.create_table('admin_notifications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('message', sa.String(), nullable=True),
    sa.Column('date_received', sa.String(), nullable=True),
    sa.Column('date_read', sa.String(), nullable=True),
    sa.Column('status', sa.Enum('read', 'unread', name='statustype'), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('admin_notifications')
    # ### end Alembic commands ###