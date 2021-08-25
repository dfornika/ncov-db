#!/usr/bin/env python

import argparse
import collections
import csv
from datetime import date
import json
import os
import sys

import sqlalchemy as sa
import sqlalchemy.orm as sao

from store_variants.model import Container


def parse_metadata_tsv(metadata_tsv_path):

    date_fields = [
        'date',
    ]

    metadata_records = []

    with open(metadata_tsv_path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            m = collections.OrderedDict()
            m['sample_id'] = row['sample']
            if row['date'] == 'NA':
                m['collection_date'] = None
            else:
                collection_date = date.fromisoformat(row['date'])
                m['collection_date'] = collection_date
            m['qpcr_ct'] = row['ct']
            metadata_records.append(m)

    return metadata_records


def store_metadata_records(session, metadata_records):
    for idx, metadata_record in enumerate(metadata_records):
        container_id = metadata_record['sample_id'].split('-')[0]

        existing_container = (
            session.query(Container)
            .filter(Container.container_id == container_id)
            .one_or_none()
        )

        if existing_container is not None and existing_container.collection_date is None:
            existing_container.collection_date = metadata_record['collection_date']
        elif existing_container is not None and args.force_update:
            existing_container.collection_date = metadata_record['collection_date']
            session.commit()
        elif not (container_id.startswith('NEG') or container_id.startswith('POS')):
            container = Container()
            container.container_id = container_id
            container.collection_date = metadata_record['collection_date']

            session.add(container)

            if idx % 1000 == 0:
                session.flush()

    session.commit()

    return None
    

def main(args):

    if args.db:
        db = args.db
    else:
        db = ':memory:'

    connection_string = "sqlite+pysqlite:///" + db
    engine = sa.create_engine(connection_string)
    Session = sao.sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    metadata_records = parse_metadata_tsv(args.metadata)

    store_metadata_records(session, metadata_records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('metadata')
    parser.add_argument('--db')
    parser.add_argument('--force-update', action='store_true')
    args = parser.parse_args()
    main(args)
