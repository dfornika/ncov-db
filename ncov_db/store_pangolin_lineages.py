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

import ncov_db.model as model



def sequencing_run_id_to_run_date(sequencing_run_id):
    run_id_date_string = sequencing_run_id.split('_')[0]
    year = '20' + run_id_date_string[0:2]
    month = run_id_date_string[2:4]
    day = run_id_date_string[4:6]
    iso8601_date_string = year + '-' + month + '-' + day
    run_date = date.fromisoformat(iso8601_date_string)
    return run_date


def sequencing_run_id_to_sequencing_run_obj(sequencing_run_id):
    sequencing_run_obj = model.SequencingRun()
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
    container_obj = model.Container()
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
    
    library_obj = model.Library()
    for key in library.keys():
        setattr(library_obj, key, library[key])

    return library_obj

def parse_pangolin_results(pangolin_results_path):

    field_translation = {
        'run_id': 'sequencing_run_id',
        'sample_id': 'library_id',
        'lineage': 'lineage',
        'conflict': 'conflict',
        'ambiguity_score': 'ambiguity_score',
        'scorpio_call': 'scorpio_call',
        'scorpio_support': 'scorpio_support',
        'scorpio_conflict': 'scorpio_conflict',
        'version': 'version',
        'pangolin_version': 'pangolin_version',
        'pangoLEARN_version': 'pangolearn_version',
        'pango_version': 'pango_version',
        'status': 'status',
        'note': 'note',
    }
    
    float_fields = [
        'conflict',
        'ambiguity_score',
        'scorpio_support',
        'scorpio_conflict',
    ]
    
    pangolin_results = []

    with open(pangolin_results_path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            p = collections.OrderedDict()
            for k, v in field_translation.items():
                if row[k] == '':
                    p[v] = None
                else:
                    p[v] = row[k]
            
            for f in float_fields:
                if p[f]:
                    p[f] = float(p[f])
            
            pangolin_result_obj = model.PangolinResult()
            for key in p.keys():
                setattr(pangolin_result_obj, key, p[key])

            pangolin_results.append(pangolin_result_obj)

    return pangolin_results


def store_sequencing_run(session, sequencing_run_id):
    existing_run = (
        session.query(model.SequencingRun)
        .filter(
            model.SequencingRun.sequencing_run_id == sequencing_run_id
        )
        .one_or_none()
    )

    if existing_run is None:
        new_sequencing_run = sequencing_run_id_to_sequencing_run_obj(sequencing_run_id)
        session.add(new_sequencing_run)
        session.commit()


def store_pangolin_results(session, pangolin_results):
    for idx, pangolin_result in enumerate(pangolin_results):
        container_id = library_id_to_container_id(pangolin_result.library_id)
        if container_id:
            existing_container = (
                session.query(model.Container)
                .filter(
                    sa.and_(
                        model.Container.container_id == container_id
                    )
                )
                .one_or_none()
            )

            if existing_container is None:
                new_container = library_id_to_container_obj(pangolin_result.library_id)
                session.add(new_container)
    
        existing_library = (
            session.query(model.Library)
            .filter(
                sa.and_(
                    model.Library.library_id == pangolin_result.library_id
                )
            )
            .one_or_none()
        )

        if existing_library is None:
            new_library = library_id_to_library_obj(pangolin_result.library_id)
            session.add(new_library)

        existing_pangolin_result = (
            session.query(model.PangolinResult)
            .filter(
                sa.and_(
                    model.PangolinResult.sequencing_run_id == pangolin_result.sequencing_run_id,
                    model.PangolinResult.library_id == pangolin_result.library_id,
                    model.PangolinResult.version == pangolin_result.version,
                    model.PangolinResult.pangolin_version == pangolin_result.pangolin_version,
                    model.PangolinResult.pangolearn_version == pangolin_result.pangolearn_version,
                    model.PangolinResult.pango_version == pangolin_result.pango_version,
                )
            )
            .one_or_none()
        )
    
        if existing_pangolin_result is None:
            session.add(pangolin_result)

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

    pangolin_results = parse_pangolin_results(args.pangolin_results)

    sequencing_run_ids = set()

    for pangolin_result in pangolin_results:
        sequencing_run_ids.add(pangolin_result.sequencing_run_id)

    for sequencing_run_id in sequencing_run_ids:
        store_sequencing_run(session, sequencing_run_id)

    store_pangolin_results(session, pangolin_results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pangolin_results')
    parser.add_argument('--db')
    args = parser.parse_args()
    main(args)
