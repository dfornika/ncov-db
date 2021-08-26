"""create sequencing run table

Revision ID: dde3260bdeda
Revises: 7a1bfada27af
Create Date: 2021-08-24 14:51:53.787857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dde3260bdeda'
down_revision = '7a1bfada27af'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'sequencing_run',
        sa.Column('sequencing_run_id', sa.String, primary_key=True),
        sa.Column('run_date',          sa.Date),
        sa.Column('platform',          sa.String),
        sa.Column('instrument_id',     sa.String),
    )


def downgrade():
    op.drop_table('sequencing_run')
