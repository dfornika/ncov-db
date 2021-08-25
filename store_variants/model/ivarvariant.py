import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class IvarVariant(Base):
    __tablename__ = "variant_ivar"
    library_id                     = sa.Column(sa.String, primary_key=True)
    variant_calling_tool           = sa.Column(sa.String, primary_key=True)
    variant_calling_tool_version   = sa.Column(sa.String, primary_key=True)
    ref_accession                  = sa.Column(sa.String, primary_key=True)
    position                       = sa.Column(sa.Integer, primary_key=True)
    ref_allele                     = sa.Column(sa.String, primary_key=True)
    alt_allele                     = sa.Column(sa.String, primary_key=True)
    ref_allele_depth               = sa.Column(sa.Integer)
    ref_allele_depth_reverse_reads = sa.Column(sa.Integer)
    ref_allele_mean_quality        = sa.Column(sa.Integer)
    alt_allele_depth               = sa.Column(sa.Integer)
    alt_allele_depth_reverse_reads = sa.Column(sa.Integer)
    alt_allele_mean_quality        = sa.Column(sa.Integer)
    alt_allele_frequency           = sa.Column(sa.Float)
    consensus_allele               = sa.Column(sa.String)
    variant_type                   = sa.Column(sa.String)
    is_ambiguous                   = sa.Column(sa.Boolean)
    total_depth                    = sa.Column(sa.Integer)
    p_value_fishers_exact          = sa.Column(sa.Float)
    p_value_pass                   = sa.Column(sa.Boolean)
    gff_feature                    = sa.Column(sa.String)
    ref_codon                      = sa.Column(sa.String)
    ref_amino_acid                 = sa.Column(sa.String)
    alt_codon                      = sa.Column(sa.String)
    alt_amino_acid                 = sa.Column(sa.String)
