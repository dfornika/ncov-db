"""create variant_ivar table

Revision ID: 45aeb447b7ac
Revises: e0d9e28f6c3c
Create Date: 2021-08-17 16:17:52.051397

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45aeb447b7ac'
down_revision = 'e0d9e28f6c3c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'variant_ivar',
        sa.Column('library_id',                     sa.String, sa.ForeignKey('library.id'), primary_key=True),
        sa.Column('variant_calling_tool',           sa.String, primary_key=True),
        sa.Column('variant_calling_tool_version',   sa.String, primary_key=True),
        sa.Column('ref_accession',                  sa.String, primary_key=True),
        sa.Column('nucleotide_position',            sa.Integer, primary_key=True),
        sa.Column('ref_allele',                     sa.String, primary_key=True),
        sa.Column('alt_allele',                     sa.String, primary_key=True),
        sa.Column('ref_allele_depth',               sa.Integer),
        sa.Column('ref_allele_depth_reverse_reads', sa.Integer),
        sa.Column('ref_allele_mean_quality',        sa.Integer),
        sa.Column('alt_allele_depth',               sa.Integer),
        sa.Column('alt_allele_depth_reverse_reads', sa.Integer),
        sa.Column('alt_allele_mean_quality',        sa.Integer),
        sa.Column('alt_allele_frequency',           sa.Float),
        sa.Column('consensus_allele',               sa.String),
        sa.Column('variant_type',                   sa.String),
        sa.Column('is_ambiguous',                   sa.Boolean),
        sa.Column('total_depth',                    sa.Integer),
        sa.Column('p_value_fishers_exact',          sa.Float),
        sa.Column('p_value_pass',                   sa.Boolean),
        sa.Column('gene_name',                      sa.String),
        sa.Column('ref_codon',                      sa.String),
        sa.Column('ref_amino_acid',                 sa.String),
        sa.Column('alt_codon',                      sa.String),
        sa.Column('alt_amino_acid',                 sa.String),
        sa.Column('codon_position',                 sa.Integer),
        sa.Column('mutation_name_by_amino_acid',    sa.String),
    )


def downgrade():
    op.drop_table('variant_ivar')
