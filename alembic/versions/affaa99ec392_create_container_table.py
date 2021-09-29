"""create container table

Revision ID: affaa99ec392
Revises:
Create Date: 2021-08-23 12:43:52.407810

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'affaa99ec392'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'container',
        sa.Column('id',              sa.String, primary_key=True),
        sa.Column('collection_date', sa.Date),
    )


def downgrade():
    op.drop_table('container')
