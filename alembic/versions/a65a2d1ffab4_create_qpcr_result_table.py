"""create qpcr result table

Revision ID: a65a2d1ffab4
Revises: 1587268b560f
Create Date: 2021-08-25 17:03:43.931356

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a65a2d1ffab4'
down_revision = '1587268b560f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'qpcr_result',
        sa.Column('container_id', sa.String, sa.ForeignKey('container.container_id'), primary_key=True),
        sa.Column('ct_value',     sa.Float),
    )


def downgrade():
    op.drop_table('qpcr_result')
