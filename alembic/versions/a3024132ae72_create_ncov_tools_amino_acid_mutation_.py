"""create ncov tools amino acid mutation table

Revision ID: a3024132ae72
Revises: a65a2d1ffab4
Create Date: 2021-08-26 19:30:27.841286

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3024132ae72'
down_revision = 'a65a2d1ffab4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'ncov_tools_amino_acid_mutation',
        sa.Column('library_id',                  sa.String, sa.ForeignKey('library.id'), primary_key=True),
        sa.Column('ref_accession',               sa.String, primary_key=True),
        sa.Column('nucleotide_position',         sa.Integer, primary_key=True),
        sa.Column('ref_allele',                  sa.Integer, primary_key=True),
        sa.Column('alt_allele',                  sa.Integer, primary_key=True),
        sa.Column('consequence',                 sa.String),
        sa.Column('gene',                        sa.String),
        sa.Column('ref_amino_acid',              sa.String),
        sa.Column('alt_amino_acid',              sa.String),
        sa.Column('codon_position',              sa.Integer),
        sa.Column('mutation_name_by_amino_acid', sa.String),
    )


def downgrade():
    op.drop_table('ncov_tools_amino_acid_mutation')
