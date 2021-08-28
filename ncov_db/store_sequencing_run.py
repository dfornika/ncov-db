#!/usr/bin/env python

import argparse
import collections
import datetime
import json
import os
import pathlib

import ncov_db.store_metadata_tsv
import ncov_db.store_variants_tsv
import ncov_db.store_ncov_tools_summary_qc
import ncov_db.store_ncov_tools_amino_acid_mutation_table

def now():
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat()
    return now

def percent(n, d):
    pct = round(n  / d * 100, 2)
    return pct

def main(args):

    log_msg = collections.OrderedDict()
    log_msg['timestamp'] = now()
    log_msg['event_type'] = 'load_run_started'
    log_msg['run_dir'] = os.path.abspath(args.run_dir)
    print(json.dumps(log_msg))

    artic_version = '1.3'
    ncov_tools_version = '1.5'
    
    store_metadata_args = {
        'db': args.db,
    }

    metadata_files = list(pathlib.Path(args.run_dir).rglob('metadata.tsv'))
    total_metadata_files = len(metadata_files)
    for n, f in enumerate(metadata_files):
        store_metadata_args['metadata'] = f
        ncov_db.store_metadata_tsv.main(None, store_metadata_args)
        log_msg = collections.OrderedDict()
        log_msg['timestamp'] = now()
        log_msg['event_type'] = 'file_loaded'
        log_msg['file_type'] = 'metadata_tsv'
        log_msg['filename'] = os.path.basename(f)
        log_msg['progress_pct'] = percent((n + 1), total_metadata_files)
        print(json.dumps(log_msg))


    store_ivar_variants_args = {
        'db': args.db,
    }

    ivar_variants_dir = os.path.join(
        args.run_dir,
        'ncov2019-artic-nf-v' + artic_version + '-output',
        'ncovIllumina_sequenceAnalysis_addCodonPositionToVariants',
    )
    
    ivar_variant_files = list(pathlib.Path(ivar_variants_dir).rglob('*.tsv'))
    total_ivar_variant_files = len(ivar_variant_files)
    for n, f in enumerate(ivar_variant_files):
        store_ivar_variants_args['variants'] = f
        ncov_db.store_variants_tsv.main(None, store_ivar_variants_args)
        log_msg = collections.OrderedDict()
        log_msg['timestamp'] = now()
        log_msg['event_type'] = 'file_loaded'
        log_msg['file_type'] = 'ivar_variants_tsv'
        log_msg['filename'] = os.path.basename(f)
        log_msg['progress_pct'] = percent((n + 1), total_ivar_variant_files)
        print(json.dumps(log_msg))


    store_ncov_tools_summary_qc_args = {
        'db': args.db,
    }
    
    ncov_tools_qc_output_dir = os.path.join(
        args.run_dir,
        'ncov2019-artic-nf-v' + artic_version + '-output',
        'ncov-tools-v' + ncov_tools_version + '-output',
    )

    ncov_tools_qc_reports_dir = os.path.join(
        ncov_tools_qc_output_dir,
        'qc_reports',
    )
    
    ncov_tools_summary_qc = list(pathlib.Path(ncov_tools_qc_reports_dir).rglob('*_summary_qc.tsv'))
    total_ncov_tools_summary_qc_files = len(ncov_tools_summary_qc)
    for n, f in enumerate(ncov_tools_summary_qc):
        store_ncov_tools_summary_qc_args['qc_summary'] = f
        ncov_db.store_ncov_tools_summary_qc.main(None, store_ncov_tools_summary_qc_args)
        log_msg = collections.OrderedDict()
        log_msg['timestamp'] = now()
        log_msg['event_type'] = 'file_loaded'
        log_msg['file_type'] = 'ncov_tools_summary_qc'
        log_msg['filename'] = os.path.basename(f)
        log_msg['progress_pct'] = percent((n + 1), total_ncov_tools_summary_qc_files)
        print(json.dumps(log_msg))
    

    store_ncov_tools_aa_mutation_args = {
        'db': args.db,
    }
    ncov_tools_aa_tables = list(pathlib.Path(ncov_tools_qc_output_dir).rglob('by_plate/*/qc_annotation/*_aa_table.tsv'))
    total_ncov_tools_aa_table_files = len(ncov_tools_aa_tables)
    for n, f in enumerate(ncov_tools_aa_tables):
        store_ncov_tools_aa_mutation_args['ncov_tools_aa_table'] = f
        ncov_db.store_ncov_tools_amino_acid_mutation_table.main(None, store_ncov_tools_aa_mutation_args)
        log_msg = collections.OrderedDict()
        log_msg['timestamp'] = now()
        log_msg['event_type'] = 'file_loaded'
        log_msg['file_type'] = 'ncov_tools_aa_table'
        log_msg['filename'] = os.path.basename(f)
        log_msg['progress_pct'] = percent((n + 1), total_ncov_tools_aa_table_files)
        print(json.dumps(log_msg))

    log_msg = collections.OrderedDict()
    log_msg['timestamp'] = now()
    log_msg['event_type'] = 'load_run_completed'
    log_msg['run_dir'] = os.path.abspath(args.run_dir)
    print(json.dumps(log_msg))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir')
    parser.add_argument('--db', required=True)
    args = parser.parse_args()
    main(args)
