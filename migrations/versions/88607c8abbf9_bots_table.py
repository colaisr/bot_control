"""bots table

Revision ID: 88607c8abbf9
Revises: 6c50ca666286
Create Date: 2020-06-04 14:21:09.456505

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88607c8abbf9'
down_revision = '6c50ca666286'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bots',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('is_running', sa.Boolean(), server_default='0', nullable=False),
    sa.Column('name', sa.String(length=255, collation='NOCASE'), server_default='', nullable=False),
    sa.Column('api_key', sa.String(length=255, collation='NOCASE'), server_default='', nullable=False),
    sa.Column('calendar_id', sa.String(length=255, collation='NOCASE'), server_default='', nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('bots')
    # ### end Alembic commands ###
