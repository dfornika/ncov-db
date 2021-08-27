#!/usr/bin/env python

import argparse
import os
import pathlib

import store_variants.store_metadata_tsv
import store_variants.store_variants_tsv
import store_variants.store_ncov_tools_summary_qc

def main(args):

    artic_version = '1.3'
    ncov_tools_version = '1.5'
    
    store_metadata_args = {
        'db': args.db,
        'metadata': os.path.join(args.run_dir, 'metadata.tsv'),
    }
    store_variants.store_metadata_tsv.main(None, store_metadata_args)


    store_ivar_variants_args = {
        'db': args.db,
    }

    ivar_variants_dir = os.path.join(
        args.run_dir,
        'ncov2019-artic-nf-v' + artic_version + '-output',
        'ncovIllumina_sequenceAnalysis_addCodonPositionToVariants',
    )
    
    ivar_variant_files = pathlib.Path(ivar_variants_dir).rglob('*.tsv')
    for f in ivar_variant_files:
        store_ivar_variants_args['variants'] = f
        store_variants.store_variants_tsv.main(None, store_ivar_variants_args)


    store_ncov_tools_summary_qc_args = {
        'db': args.db,
    }
    
    ncov_tools_qc_reports_dir = os.path.join(
        args.run_dir,
        'ncov2019-artic-nf-v' + artic_version + '-output',
        'ncov-tools-v' + ncov_tools_version + '-output',
        'qc_reports',
    )
    ncov_tools_summary_qc = pathlib.Path(ncov_tools_qc_reports_dir).rglob('*_summary_qc.tsv')
    for f in ncov_tools_summary_qc:
        store_ncov_tools_summary_qc_args['qc_summary'] = f
        store_variants.store_ncov_tools_summary_qc.main(None, store_ncov_tools_summary_qc_args)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir')
    parser.add_argument('--db', required=True)
    args = parser.parse_args()
    main(args)
