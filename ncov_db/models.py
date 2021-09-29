from typing import Optional

from sqlmodel import Field, SQLModel, create_engine

from datetime import date
import sqlalchemy as sa
import sqlalchemy.orm as sao
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Container(SQLModel, table=True):
    __tablename__ = "container"
    id: str = Field(primary_key=True)
    collection_date: date


class Library(SQLModel, table=True):
    __tablename__ = "library"
    id: str = Field(primary_key=True)
    container_id: str = Field(foreign_key='container.id')
    library_plate_id: int
    index_set_id: str
    plate_well: str
    plate_row: str
    plate_col: int


class QpcrResult(SQLModel, table=True):
    __tablename__ = "qpcr_result"
    container_id: str = Field(foreign_key='container.id', primary_key=True)
    ct_value: float


class SequencingRun(SQLModel, table=True):
    __tablename__ = "sequencing_run"
    id: str = Field(primary_key=True)
    run_date: date
    platform: str
    instrument_id: str


class NcovToolsSummaryQC(SQLModel, table=True):
    __tablename__ = "ncov_tools_summary_qc"
    library_id: str = Field(foreign_key='library.id', primary_key=True)
    sequencing_run_id: str = Field(foreign_key='sequencing_run.id', primary_key=True)
    num_consensus_snvs: int
    num_consensus_n: int
    num_consensus_iupac: int
    num_variants_snvs: int
    num_variants_indel: int
    num_variants_indel_triplet: int
    mean_sequencing_depth: float
    median_sequencing_depth: int
    genome_completeness: float
    qc_flags: str
    qc_pass: bool

    
class Ncov2019ArticNfQC(SQLModel, table=True):
    __tablename__ = "ncov2019_artic_nf_qc"
    library_id: str = Field(foreign_key='library.id', primary_key=True)
    percent_n_bases: float
    genome_completeness: float
    longest_no_n_run: int
    num_aligned_reads: int
    qc_pass: bool


class DownsamplingReport(SQLModel, table=True):
    __tablename__ = "downsampling_report"
    library_id: str = Field(foreign_key='library.id', primary_key=True)
    total_input_reads: int
    reads_processed: int
    reads_written: int
    reads_discarded: int
    downsampling_factor: float


class VariantIvar(SQLModel, table=True):
    __tablename__ = "variant_ivar"
    library_id: str = Field(foreign_key='library.id', primary_key=True)
    variant_calling_tool: str = Field(primary_key=True)
    variant_calling_tool_version: str = Field(primary_key=True)
    ref_accession: str = Field(primary_key=True)
    nucleotide_position: int = Field(primary_key=True)
    ref_allele: str = Field(primary_key=True)
    alt_allele: str = Field(primary_key=True)
    ref_allele_depth: int
    ref_allele_depth_reverse_reads: int
    ref_allele_mean_quality: int
    alt_allele_depth: int
    alt_allele_depth_reverse_reads: int
    alt_allele_mean_quality: int
    alt_allele_frequency: float
    consensus_allele: str
    variant_type: str
    is_ambiguous: bool
    total_depth: int
    p_value_fishers_exact: float
    p_value_pass: bool
    gene_name: Optional[str] = None
    ref_codon: Optional[str] = None
    ref_amino_acid: Optional[str] = None
    alt_codon: Optional[str] = None
    alt_amino_acid: Optional[str] = None
    codon_position: Optional[int] = None
    mutation_name_by_amino_acid: Optional[str] = None


class VariantFreebayes(SQLModel, table=True):
    __tablename__ = "variant_freebayes"
    library_id: str = Field(foreign_key='library.id', primary_key=True)
    variant_calling_tool: str = Field(primary_key=True)
    variant_calling_tool_version: str = Field(primary_key=True)
    ref_accession: str = Field(primary_key=True)
    nucleotide_position: int = Field(primary_key=True)
    ref_allele: str = Field(primary_key=True)
    alt_allele: str = Field(primary_key=True)
    ref_allele_depth: int
    ref_allele_depth_reverse_reads: int
    ref_allele_mean_quality: int
    alt_allele_depth: int
    alt_allele_depth_reverse_reads: int
    alt_allele_mean_quality: int
    alt_allele_frequency: float
    consensus_allele: str
    annotation: str
    impact: str
    variant_type: str
    is_ambiguous: bool
    total_depth: int
    gene_name: Optional[str] = None
    feature_id: Optional[str] = None
    transcript_biotype: Optional[str] = None
    nucleotide_change: Optional[str] = None
    amino_acid_change: Optional[str] = None
    cds_position: Optional[int] = None
    cds_length: Optional[int] = None
    amino_acid_position: Optional[int] = None
    amino_acid_length: Optional[int] = None
    annotation_errors_warnings_info: Optional[str] = None


class NcovToolsAminoAcidMutation(SQLModel, table=True):
    __tablename__ = "ncov_tools_amino_acid_mutation"
    library_id: str = Field(foreign_key='library.id', primary_key=True)
    ref_accession: str = Field(primary_key=True)
    nucleotide_position: int = Field(primary_key=True)
    ref_allele: int = Field(primary_key=True)
    alt_allele: int = Field(primary_key=True)
    consequence: str
    gene: str
    ref_amino_acid: str
    alt_amino_acid: str
    codon_position: int
    mutation_name_by_amino_acid: str


class PangolinResult(SQLModel, table=True):
    __tablename__ = "pangolin_result"
    sequencing_run_id: str  = Field(foreign_key='sequencing_run.id', primary_key=True)
    library_id: str = Field(foreign_key='library.id', primary_key=True)
    lineage: str
    conflict: float
    ambiguity_score: float
    scorpio_call: str
    scorpio_support: float
    scorpio_conflict: float
    version: str = Field(primary_key=True)
    pangolin_version: str = Field(primary_key=True)
    pangolearn_version: str = Field(primary_key=True)
    pango_version: str = Field(primary_key=True)
    status: str
    note: str
