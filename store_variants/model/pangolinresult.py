import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PangolinResult(Base):
    __tablename__ = "pangolin_result"
    sequencing_run_id  = sa.Column(sa.String, primary_key=True)
    library_id         = sa.Column(sa.String, primary_key=True)
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
