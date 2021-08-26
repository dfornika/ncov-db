"""create summary qc table

Revision ID: 7a1bfada27af
Revises: 45aeb447b7ac
Create Date: 2021-08-24 10:31:11.167522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a1bfada27af'
down_revision = '45aeb447b7ac'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ncov_tools_summary_qc',
        sa.Column('library_id',                 sa.String, sa.ForeignKey('library.library_id'), primary_key=True),
        sa.Column('sequencing_run_id',          sa.String, sa.ForeignKey('sequencing_run.sequencing_run_id'), primary_key=True),
        sa.Column('num_consensus_snvs',         sa.Integer),
        sa.Column('num_consensus_n',            sa.Integer),
        sa.Column('num_consensus_iupac',        sa.Integer),
        sa.Column('num_variants_snvs',          sa.Integer),
        sa.Column('num_variants_indel',         sa.Integer),
        sa.Column('num_variants_indel_triplet', sa.Integer),
        sa.Column('mean_sequencing_depth',      sa.Float),
        sa.Column('median_sequencing_depth',    sa.Integer),
        sa.Column('genome_completeness',        sa.Float),
        sa.Column('qc_flags',                   sa.String),
        sa.Column('qc_pass',                    sa.Boolean),
    )


def downgrade():
    op.drop_table('summary_qc')
