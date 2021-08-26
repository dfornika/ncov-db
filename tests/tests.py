#!/usr/bin/env python

import os
import string

from datetime import date

import alembic
import alembic.config
import sqlalchemy as sa
import sqlalchemy.orm as sao

from hypothesis import settings, example, given, Verbosity, strategies as st
from hypothesis_sqlalchemy import tabular

import store_variants.model as model


connection_string = "sqlite+pysqlite:///:memory:"
engine = sa.create_engine(connection_string)


alembic_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../alembic') 
print('Running DB migrations in {:s} on {:s}'.format(alembic_dir, connection_string))
alembic_cfg = alembic.config.Config(os.path.join(alembic_dir, '../alembic.ini'))
alembic_cfg.set_main_option('script_location', alembic_dir)
alembic_cfg.set_main_option('sqlalchemy.url', connection_string)
alembic_cfg.set_section_option("logger_alembic", "level", "ERROR")

with engine.begin() as connection:    
    alembic_cfg.attributes['connection'] = connection
    alembic.command.upgrade(alembic_cfg, 'head')


# Un-comment to print db schema after migrations
# inspector = sa.inspect(engine)
# schemas = inspector.get_schema_names()

#for schema in schemas:
#    print("schema: {:s}".format(schema))
#    for table_name in inspector.get_table_names(schema=schema):
#        for column in inspector.get_columns(table_name, schema=schema):
#            print("Column: %s" % column)

def test_truism():
    assert 1 == 1


@given(st.integers())
@example(0)
@settings(verbosity=Verbosity.normal)
def test_hypothesis_truism(n):
    assert n == n

@given(
    container_id=st.text(alphabet=string.ascii_uppercase + string.digits, min_size=10, max_size=12),
    collection_date=st.dates(min_value=date.fromisoformat('2020-01-01'), max_value=date.fromisoformat('2050-01-01')),
)
@settings(
    max_examples=100,
    verbosity=Verbosity.normal,
    deadline=None,
)
def test_hypothesis_sqlalchemy(container_id, **kwargs):
    Session = sao.sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    created_container = model.Container()
    created_container.container_id=container_id
    created_container.collection_date=kwargs['collection_date']

    existing_container = (
        session.query(model.Container)
        .filter(model.Container.container_id == container_id)
        .one_or_none()
    )

    if existing_container is None:
        session.add(created_container)
        session.commit()
        
    retrieved_container = (
        session.query(model.Container)
        .filter(model.Container.container_id == container_id)
        .one_or_none()
    )

    assert retrieved_container.container_id == created_container.container_id


if __name__ == "__main__":
    
    test_truism()
    test_hypothesis_truism()
    test_hypothesis_sqlalchemy()

