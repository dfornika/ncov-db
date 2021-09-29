"""create pangolin result table

Revision ID: 1587268b560f
Revises: dde3260bdeda
Create Date: 2021-08-24 22:00:17.032944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1587268b560f'
down_revision = 'dde3260bdeda'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pangolin_result',
        sa.Column('sequencing_run_id',  sa.String, sa.ForeignKey('sequencing_run.id'), primary_key=True),
        sa.Column('library_id',         sa.String, sa.ForeignKey('library.id'), primary_key=True),
        sa.Column('lineage',            sa.String),
        sa.Column('conflict',           sa.Float),
        sa.Column('ambiguity_score',    sa.Float),
        sa.Column('scorpio_call',       sa.String),
        sa.Column('scorpio_support',    sa.Float),
        sa.Column('scorpio_conflict',   sa.Float),
        sa.Column('version',            sa.String, primary_key=True),
        sa.Column('pangolin_version',   sa.String, primary_key=True),
        sa.Column('pangolearn_version', sa.String, primary_key=True),
        sa.Column('pango_version',      sa.String, primary_key=True),
        sa.Column('status',             sa.String),
        sa.Column('note',               sa.String),
    )


def downgrade():
    op.drop_table('pangolin_result')
