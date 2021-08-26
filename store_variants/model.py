import sqlalchemy as sa
import sqlalchemy.orm as sao
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Container(Base):
    __tablename__ = "container"
    container_id    = sa.Column(sa.String, primary_key=True)
    collection_date = sa.Column(sa.Date)


class Library(Base):
    __tablename__ = "library"
    library_id       = sa.Column(sa.String, primary_key=True)
    container_id     = sa.Column(sa.String, sa.ForeignKey('container.container_id'))
    library_plate_id = sa.Column(sa.Integer)
    index_set_id     = sa.Column(sa.String)
    plate_well       = sa.Column(sa.String)
    plate_row        = sa.Column(sa.String)
    plate_col        = sa.Column(sa.Integer)


class QpcrResult(Base):
    __tablename__ = "qpcr_result"
    container_id = sa.Column(sa.String, sa.ForeignKey('container.container_id'), primary_key=True)
    target       = sa.Column(sa.String)
    ct_value     = sa.Column(sa.Float)


class SequencingRun(Base):
    __tablename__ = "sequencing_run"
    sequencing_run_id = sa.Column(sa.String, primary_key=True)
    run_date          = sa.Column(sa.Date)
    platform          = sa.Column(sa.String)
    instrument_id     = sa.Column(sa.String)


class NcovToolsSummaryQC(Base):
    __tablename__ = "ncov_tools_summary_qc"
    library_id                 = sa.Column(sa.String, sa.ForeignKey('library.library_id'), primary_key=True)
    sequencing_run_id          = sa.Column(sa.String, sa.ForeignKey('sequencing_run.sequencing_run_id'), primary_key=True)
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


class VariantIvar(Base):
    __tablename__ = "variant_ivar"
    library_id                     = sa.Column(sa.String, sa.ForeignKey('library.library_id'), primary_key=True)
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


class PangolinResult(Base):
    __tablename__ = "pangolin_result"
    sequencing_run_id  = sa.Column(sa.String, sa.ForeignKey('sequencing_run.sequencing_run_id'), primary_key=True)
    library_id         = sa.Column(sa.String, sa.ForeignKey('library.library_id'), primary_key=True)
    lineage            = sa.Column(sa.String)
    conflict           = sa.Column(sa.Float)
    ambiguity_score    = sa.Column(sa.Float)
    scorpio_call       = sa.Column(sa.String)
    scorpio_support    = sa.Column(sa.Float)
    scorpio_conflict   = sa.Column(sa.Float)
    version            = sa.Column(sa.String, primary_key=True)
    pangolin_version   = sa.Column(sa.String, primary_key=True)
    pangolearn_version = sa.Column(sa.String, primary_key=True)
    pango_version      = sa.Column(sa.String, primary_key=True)
    status             = sa.Column(sa.String)
    note               = sa.Column(sa.String)
