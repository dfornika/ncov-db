import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SequencingRun(Base):
    __tablename__ = "sequencing_run"
    sequencing_run_id = sa.Column(sa.String, primary_key=True)
    run_date          = sa.Column(sa.Date)
    platform          = sa.Column(sa.String)
    instrument_id     = sa.Column(sa.String)
