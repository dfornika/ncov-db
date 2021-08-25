import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Library(Base):
    __tablename__ = "library"
    library_id       = sa.Column(sa.String, primary_key=True)
    container_id     = sa.Column(sa.String)
    library_plate_id = sa.Column(sa.Integer)
    index_set_id     = sa.Column(sa.String)
    plate_well       = sa.Column(sa.String)
    plate_row        = sa.Column(sa.String)
    plate_col        = sa.Column(sa.Integer)
