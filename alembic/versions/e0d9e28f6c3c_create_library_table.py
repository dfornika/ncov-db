"""create library table

Revision ID: e0d9e28f6c3c
Revises: affaa99ec392
Create Date: 2021-08-23 12:47:07.827557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0d9e28f6c3c'
down_revision = 'affaa99ec392'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'library',
        sa.Column('id',               sa.String, primary_key=True),
        sa.Column('container_id',     sa.String, sa.ForeignKey('container.container_id')),
        sa.Column('library_plate_id', sa.Integer),
        sa.Column('index_set_id',     sa.String),
        sa.Column('plate_well',       sa.String),
        sa.Column('plate_row',        sa.String),
        sa.Column('plate_col',        sa.Integer),
    )


def downgrade():
    op.drop_table('library')
