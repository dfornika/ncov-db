#!/usr/bin/env python

import argparse
import os
import pathlib

import ncov_db.store_metadata_tsv
import ncov_db.store_variants_tsv
import ncov_db.store_ncov_tools_summary_qc
import ncov_db.store_ncov_tools_amino_acid_mutation_table

def main(args):

    artic_version = '1.3'
    ncov_tools_version = '1.5'
    
    store_metadata_args = {
        'db': args.db,
        'metadata': os.path.join(args.run_dir, 'metadata.tsv'),
    }
    ncov_db.store_metadata_tsv.main(None, store_metadata_args)


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
        print('[' + str(n + 1) + ' / ' + str(total_ivar_variant_files) + ']: ' + os.path.basename(f))
        store_ivar_variants_args['variants'] = f
        ncov_db.store_variants_tsv.main(None, store_ivar_variants_args)


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
        print('[' + str(n + 1) + ' / ' + str(total_ncov_tools_summary_qc_files) + ']: ' + os.path.basename(f))
        store_ncov_tools_summary_qc_args['qc_summary'] = f
        ncov_db.store_ncov_tools_summary_qc.main(None, store_ncov_tools_summary_qc_args)
    

    store_ncov_tools_aa_mutation_args = {
        'db': args.db,
    }
    ncov_tools_aa_tables = list(pathlib.Path(ncov_tools_qc_output_dir).rglob('by_plate/*/qc_annotation/*_aa_table.tsv'))
    total_ncov_tools_aa_table_files = len(ncov_tools_aa_tables)
    for n, f in enumerate(ncov_tools_aa_tables):
        print('[' + str(n + 1) + ' / ' + str(total_ncov_tools_aa_table_files) + ']: ' + os.path.basename(f))
        store_ncov_tools_aa_mutation_args['ncov_tools_aa_table'] = f
        ncov_db.store_ncov_tools_amino_acid_mutation_table.main(None, store_ncov_tools_aa_mutation_args)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir')
    parser.add_argument('--db', required=True)
    args = parser.parse_args()
    main(args)
