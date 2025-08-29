"""add participant photo

Revision ID: 2a6f9b3d9d2a
Revises: bb261ad04708
Create Date: 2025-08-29 17:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a6f9b3d9d2a'
down_revision = 'bb261ad04708'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('participant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo', sa.String(length=256), nullable=True))


def downgrade():
    with op.batch_alter_table('participant', schema=None) as batch_op:
        batch_op.drop_column('photo')

