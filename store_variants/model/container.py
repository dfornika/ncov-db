import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Container(Base):
    __tablename__ = "container"
    container_id    = sa.Column(sa.String, primary_key=True)
    collection_date = sa.Column(sa.Date)
