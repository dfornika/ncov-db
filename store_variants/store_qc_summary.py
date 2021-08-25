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

from store_variants.model.qcsummary import QCSummary
from store_variants.model.container import Container
from store_variants.model.library import Library
from store_variants.model.sequencingrun import SequencingRun


def sequencing_run_id_to_sequencing_run_obj(sequencing_run_id):
    sequencing_run_obj = SequencingRun()
    sequencing_run_obj.sequencing_run_id = sequencing_run_id
    sequencing_run_obj.run_date = sequencing_run_id_to_run_date(sequencing_run_id)
    sequencing_run_obj.instrument_id = sequencing_run_id.split('_')[1]
    if sequencing_run_obj.instrument_id.startswith('M'):
        sequencing_run_obj.platform = 'MISEQ'
    elif sequencing_run_obj.instrument_id.startswith('V'):
        sequencing_run_obj.platform = 'NEXTSEQ'
    return sequencing_run_obj


def library_id_to_container_id(library_id):
    container_id = None
    if not (library_id.startswith('POS') or library_id.startswith('NEG')):
        container_id = library_id.split('-')[0]
    return container_id


def library_id_to_container_obj(library_id):
    container_obj = Container()
    container_obj.container_id = library_id_to_container_id(library_id)
    return container_obj


def library_id_to_library_obj(library_id):
    library = {}
    library_id_components = library_id.split('-')

    library['library_id'] = library_id
    if library_id.startswith('POS'):
        library['container_id'] = None
        library['library_plate_id'] = library_id_components[2]
        library['plate_well'] = 'G12'
    elif library_id.startswith('NEG'):
        library['container_id'] = None
        library['library_plate_id'] = library_id_components[2]
        library['plate_well'] = 'H12'
    else:
        library['container_id'] = library_id_components[0]
        library['library_plate_id'] = library_id_components[1]
        library['index_set_id'] = library_id_components[2]
        library['plate_well'] = library_id_components[3]
    library['plate_row'] = library['plate_well'][0]
    library['plate_col'] = int(library['plate_well'][-2:])
    
    library_obj = Library()
    for key in library.keys():
        setattr(library_obj, key, library[key])

    return library_obj

def parse_qc_summary_tsv(qc_summary_tsv_path):

    int_fields = [
        'num_consensus_snvs',
        'num_consensus_n',
        'num_consensus_iupac',
        'num_variants_snvs',
        'num_variants_indel',
        'num_variants_indel_triplet',
        'median_sequencing_depth',
    ]

    float_fields = [
        'mean_sequencing_depth',
        'genome_completeness',
    ]
    
    qc_summaries = []

    with open(qc_summary_tsv_path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            q = collections.OrderedDict()
            q['library_id'] = row['sample']
            q['sequencing_run_id'] = row['run_name']
            qc_flags = row['qc_pass'].split(',')

            q['qc_flags'] = row['qc_pass']
            q['qc_pass'] = True
            if 'INCOMPLETE_GENOME' in qc_flags:
                q['qc_pass'] = False
            if 'PARTIAL_GENOME' in qc_flags:
                q['qc_pass'] = False

            for f in int_fields:
                q[f] = int(row[f])
            for f in float_fields:
                q[f] = float(row[f])
            
            qc_summary_obj = QCSummary()
            for key in q.keys():
                setattr(qc_summary_obj, key, q[key])

            qc_summaries.append(qc_summary_obj)

    return qc_summaries


def store_sequencing_run(session, sequencing_run_id):
    existing_run = (
        session.query(SequencingRun)
        .filter(
            SequencingRun.sequencing_run_id == sequencing_run_id
        )
        .one_or_none()
    )

    if existing_run is None:
        new_sequencing_run = sequencing_run_id_to_sequencing_run_obj(sequencing_run_id)
        session.add(new_sequencing_run)
        session.commit()


def store_qc_summary(session, qc_summary):
    container_id = library_id_to_container_id(qc_summary.library_id)
    if container_id:
        existing_container = (
            session.query(Container)
            .filter(
                sa.and_(
                    Container.container_id == container_id
                )
            )
            .one_or_none()
        )

        if existing_container is None:
            new_container = library_id_to_container_obj(qc_summary.library_id)
            session.add(new_container)
            session.commit()
    
    existing_library = (
        session.query(Library)
        .filter(
            sa.and_(
                Library.library_id == qc_summary.library_id
            )
        )
        .one_or_none()
    )

    if existing_library is None:
        new_library = library_id_to_library_obj(qc_summary.library_id)
        session.add(new_library)
        session.commit()

    existing_qc_summary = (
        session.query(QCSummary)
        .filter(
            sa.and_(
                QCSummary.sequencing_run_id == qc_summary.sequencing_run_id,
                QCSummary.library_id == qc_summary.library_id
            )
        )
        .one_or_none()
    )
    
    if existing_qc_summary is not None:
        return None
    else:
        session.add(qc_summary)
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

    qc_summaries = parse_qc_summary_tsv(args.qc_summary)

    sequencing_run_ids = set()

    for qc_summary in qc_summaries:
        sequencing_run_ids.add(qc_summary.sequencing_run_id)

    for sequencing_run_id in sequencing_run_ids:
        store_sequencing_run(session, sequencing_run_id)

    for qc_summary in qc_summaries:
        store_qc_summary(session, qc_summary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('qc_summary')
    parser.add_argument('--db')
    args = parser.parse_args()
    main(args)
