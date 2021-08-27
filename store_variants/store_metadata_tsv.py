#!/usr/bin/env python

import argparse
import collections
import csv
import json
import os
import sys

from dataclasses import dataclass
from datetime import date

import sqlalchemy as sa
import sqlalchemy.orm as sao

import store_variants.model as model


def parse_metadata_tsv(metadata_tsv_path):

    date_fields = [
        'date',
    ]

    metadata_records = []

    with open(metadata_tsv_path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            m = collections.OrderedDict()
            m['library_id'] = row['sample']
            if row['date'] == 'NA':
                m['collection_date'] = None
            else:
                collection_date = date.fromisoformat(row['date'])
                m['collection_date'] = collection_date
            if row['ct'] == 'NA':
                m['ct_value'] = None
            else:
                m['ct_value'] = row['ct']
            metadata_records.append(m)

    return metadata_records


def store_metadata_records(session, metadata_records, force_update=False):
    for idx, metadata_record in enumerate(metadata_records):
        container_id = metadata_record['library_id'].split('-')[0]

        existing_container = (
            session.query(model.Container)
            .filter(model.Container.container_id == container_id)
            .one_or_none()
        )

        if existing_container is not None and existing_container.collection_date is None:
            existing_container.collection_date = metadata_record['collection_date']
        elif existing_container is not None and force_update:
            existing_container.collection_date = metadata_record['collection_date']
            session.commit()
        elif existing_container is None:
            if not (container_id.startswith('NEG') or container_id.startswith('POS')):
                container = model.Container()
                container.container_id = container_id
                container.collection_date = metadata_record['collection_date']

                session.add(container)

        existing_qpcr_result = (
            session.query(model.QpcrResult)
            .filter(model.QpcrResult.container_id == container_id)
            .one_or_none()
        )

        if existing_qpcr_result is not None and existing_qpcr_result.ct_value is None:
            existing_qpcr_result.ct_value = metadata_record['ct_value']
        elif existing_qpcr_result is None:
            if not (metadata_record['library_id'].startswith('NEG') or metadata_record['library_id'].startswith('POS')):
                qpcr_result = model.QpcrResult()
                qpcr_result.container_id = container_id
                qpcr_result.ct_value = metadata_record['ct_value']

                session.add(qpcr_result)
        
        if idx % 1000 == 0:
            session.flush()

    session.commit()

    return None
    

def main(args, kwargs=None):
    if not args:    
        args = Args(**kwargs)

    connection_string = "sqlite+pysqlite:///" + args.db
    engine = sa.create_engine(connection_string)
    Session = sao.sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    metadata_records = parse_metadata_tsv(args.metadata)

    store_metadata_records(session, metadata_records, args.force_update)


@dataclass
class Args:
    db: str
    metadata: str
    force_update: bool = False
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('metadata')
    parser.add_argument('--db', required=True)
    parser.add_argument('--force-update', action='store_true')
    args = parser.parse_args()
    main(args)
