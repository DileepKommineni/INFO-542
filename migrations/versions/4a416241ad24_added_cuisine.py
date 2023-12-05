"""added cuisine

Revision ID: 4a416241ad24
Revises: 18a5fbb518e4
Create Date: 2023-12-04 02:08:07.942653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a416241ad24'
down_revision = '18a5fbb518e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interaction', schema=None) as batch_op:
        batch_op.drop_column('interaction_type')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('interaction', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interaction_type', sa.VARCHAR(length=10), nullable=False))

    # ### end Alembic commands ###