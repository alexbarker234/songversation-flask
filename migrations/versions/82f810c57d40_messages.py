"""messages

Revision ID: 82f810c57d40
Revises: 47dd65a8b0ad
Create Date: 2023-05-21 17:46:30.060635

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82f810c57d40'
down_revision = '47dd65a8b0ad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.String(length=120), nullable=True),
    sa.Column('reciever_id', sa.String(length=120), nullable=True),
    sa.Column('content', sa.String(length=120), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message')
    # ### end Alembic commands ###
