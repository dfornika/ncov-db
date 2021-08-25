import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class QCSummary(Base):
    __tablename__ = "summary_qc"
    library_id                 = sa.Column(sa.String, primary_key=True)
    sequencing_run_id          = sa.Column(sa.String, primary_key=True)
    num_consensus_snvs         = sa.Column(sa.Integer)
    num_consensus_n            = sa.Column(sa.Integer)
    num_consensus_iupac        = sa.Column(sa.Integer)
    num_variants_snvs          = sa.Column(sa.Integer)
    num_variants_indel         = sa.Column(sa.Integer)
    num_variants_indel_triplet = sa.Column(sa.Integer)
    mean_sequencing_depth      = sa.Column(sa.Float)
    median_sequencing_depth    = sa.Column(sa.Integer)
    genome_completeness        = sa.Column(sa.Float)
    qc_flags                   = sa.Column(sa.String)
    qc_pass                    = sa.Column(sa.Boolean)
