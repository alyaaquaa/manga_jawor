"""Remove parent_id from Comment

Revision ID: 24ed9a35e461
Revises: aebcd7adf3e1
Create Date: 2025-06-07 14:52:52.589999

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '24ed9a35e461'
down_revision = 'aebcd7adf3e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.drop_constraint('comment_ibfk_3', type_='foreignkey')
        batch_op.drop_column('parent_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('parent_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('comment_ibfk_3', 'comment', ['parent_id'], ['id'])

    # ### end Alembic commands ###
