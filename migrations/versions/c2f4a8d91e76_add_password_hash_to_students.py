"""Add password hash to students

Revision ID: c2f4a8d91e76
Revises: 91fcd477d6f8
Create Date: 2026-09-21

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2f4a8d91e76'
down_revision = '91fcd477d6f8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('students_x', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255), nullable=False))


def downgrade():
    with op.batch_alter_table('students_x', schema=None) as batch_op:
        batch_op.drop_column('password_hash')