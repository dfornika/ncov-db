#!/usr/bin/env python

import argparse
import collections
import csv
from datetime import date
import json
import os
import sys

from store_variants.model.container import Container

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

def parse_metadata_tsv(metadata_tsv_path):

    date_fields = [
        'date',
    ]

    containers = []

    with open(metadata_tsv_path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            c = collections.OrderedDict()
            container_id = row['sample'].split('-')[0]
            c['container_id'] = container_id
            if row['date'] == 'NA':
                c['collection_date'] = None
            else:
                collection_date = date.fromisoformat(row['date'])
            c['collection_date'] = collection_date

            if not (c['container_id'].startswith('POS') or c['container_id'].startswith('NEG')): 
                container_obj = Container()
                for key in c.keys():
                    setattr(container_obj, key, c[key])

                containers.append(container_obj)

    return containers


def store_container(session, container):
    existing_container = (
        session.query(Container)
        .filter(Container.container_id == container.container_id)
        .one_or_none()
    )
    
    if existing_container is not None:
        return None
    else:
        session.add(container)
        session.commit()

    return None
    

def main(args):

    if args.db:
        db = args.db
    else:
        db = ':memory:'

    connection_string = "sqlite+pysqlite:///" + db
    engine = create_engine(connection_string)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()



    containers = parse_metadata_tsv(args.metadata)

    for container in containers:
        store_container(session, container)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('metadata')
    parser.add_argument('--db')
    args = parser.parse_args()
    main(args)
