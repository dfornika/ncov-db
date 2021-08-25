#!/usr/bin/env python

import argparse
import collections
import csv
import json
import os
import sys

import sqlalchemy as sa
import sqlalchemy.orm as sao

import store_variants.model as model

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

def parse_variants_tsv(variants_tsv_path, library_id, filters):
    field_name_conversion = {
        'REGION':      'ref_accession',                 
        'POS':         'position',                      
        'REF':         'ref_allele',                    
        'ALT':         'alt_allele',                    
        'REF_DP':      'ref_allele_depth',              
        'REF_RV':      'ref_allele_depth_reverse_reads',
        'REF_QUAL':    'ref_allele_mean_quality',       
        'ALT_DP':      'alt_allele_depth',              
        'ALT_RV':      'alt_allele_depth_reverse_reads',
        'ALT_QUAL':    'alt_allele_mean_quality',       
        'ALT_FREQ':    'alt_allele_frequency',          
        'TOTAL_DP':    'total_depth',                   
        'PVAL':        'p_value_fishers_exact',         
        'PASS':        'p_value_pass',                  
        'GFF_FEATURE': 'gff_feature',                   
        'REF_CODON':   'ref_codon',                     
        'REF_AA':      'ref_amino_acid',                
        'ALT_CODON':   'alt_codon',                     
        'ALT_AA':      'alt_amino_acid',                
    }

    int_fields = [
        'position',
        'ref_allele_depth',
        'ref_allele_depth_reverse_reads',
        'ref_allele_mean_quality',
        'alt_allele_depth',
        'alt_allele_depth_reverse_reads',
        'alt_allele_mean_quality',
        'total_depth',
    ]

    float_fields = [
        'alt_allele_frequency',
        'p_value_fishers_exact',
    ]

    bool_fields = [
        'p_value_pass',
    ]

    na_null_fields = [
        'gff_feature',
        'ref_codon',
        'ref_amino_acid',
        'alt_codon',
        'alt_amino_acid',
    ]

    iupac_ambiguity = {
        ('A', 'A'): 'A',
        ('A', 'C'): 'M',
        ('A', 'G'): 'R',
        ('A', 'T'): 'W',
        ('C', 'A'): 'M',
        ('C', 'C'): 'C',
        ('C', 'G'): 'S',
        ('C', 'T'): 'Y',
        ('G', 'A'): 'R',
        ('G', 'C'): 'S',
        ('G', 'G'): 'G',
        ('G', 'T'): 'K',
        ('T', 'A'): 'W',
        ('T', 'C'): 'Y',
        ('T', 'G'): 'K',
        ('T', 'T'): 'T',
    }

    variants = []

    with open(variants_tsv_path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            variant = collections.OrderedDict()
            variant['library_id'] = library_id
            variant['variant_calling_tool'] = 'ivar'
            variant['variant_calling_tool_version'] = '1.3'
            for k, v in field_name_conversion.items():
                variant[v] = row[k]
            for f in int_fields:
                variant[f] = int(variant[f])
            for f in float_fields:
                variant[f] = float(variant[f])
            for f in bool_fields:
                variant[f] = bool(variant[f])
            for f in na_null_fields:
                if variant[f] == 'NA':
                    variant[f] = None

            if len(variant['ref_allele']) == 1 and len(variant['alt_allele']) == 1:
                variant['variant_type'] = 'snp'
            elif variant['alt_allele'].startswith('+'):
                variant['variant_type'] = 'ins'
            elif variant['alt_allele'].startswith('-'):
                variant['variant_type'] = 'del'
            else:
                variant['variant_type'] = 'undetermined'

            if variant['variant_type'] == 'snp':
                try:
                    if variant['alt_allele_frequency'] < filters['min_freq_threshold']:
                        variant['consensus_allele'] = variant['ref_allele']
                    elif variant['alt_allele_frequency'] > filters['min_freq_threshold'] and variant['alt_allele_frequency'] < filters['freq_threshold']:
                        variant['consensus_allele'] = iupac_ambiguity[(variant['ref_allele'], variant['alt_allele'])]
                    elif variant['alt_allele_frequency'] > filters['freq_threshold']:
                        variant['consensus_allele'] = variant['alt_allele']
                except KeyError as e:
                    print('No consensus allele. file: ' + variants_tsv_path + ', position: ' + str(variant['position']))

            if variant['variant_type'] == 'snp':
                try:
                    if variant['consensus_allele'] in {'M', 'R', 'W', 'S', 'Y', 'K'}:
                        variant['is_ambiguous'] = True
                    else:
                        variant['is_ambiguous'] = False
                except KeyError as e:
                    print('No consensus allele. file: ' + variants_tsv_path + ', position: ' + str(variant['position']))

            variant_obj = model.VariantIvar()
            for key in variant.keys():
                setattr(variant_obj, key, variant[key])

            variants.append(variant_obj)

    return variants


def store_container_for_library(session, library):
    container_id = library.library_id.split('-')[0]
    
    existing_container = (
        session.query(model.Container)
        .filter(
            model.Container.container_id == container_id
        )
        .one_or_none()
    )

    if existing_container is None:
        container = model.Container()
        container.container_id = container_id
        session.add(container)
        session.commit()

    return None


def store_library(session, library):
    if not (library.library_id.startswith('POS') or library.library_id.startswith('NEG')):
        store_container_for_library(session, library)
    
    existing_library = (
        session.query(model.Library)
        .filter(
            model.Library.library_id == library.library_id
        )
        .one_or_none()
    )
    if existing_library is None:
        session.add(library)

    session.commit()

    return None


def store_variants(session, variants):
    for idx, variant in enumerate(variants):
        existing_variant = (
            session.query(model.VariantIvar)
            .filter(
                sa.and_(
                    model.VariantIvar.library_id == variant.library_id,
                    model.VariantIvar.variant_calling_tool == variant.variant_calling_tool,
                    model.VariantIvar.variant_calling_tool_version == variant.variant_calling_tool_version,
                    model.VariantIvar.ref_accession == variant.ref_accession,
                    model.VariantIvar.position == variant.position,
                    model.VariantIvar.ref_allele == variant.ref_allele,
                    model.VariantIvar.alt_allele == variant.alt_allele,
                )
            )
            .one_or_none()
        )
        if existing_variant is None:
            session.add(variant)
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
    
    library_id = os.path.basename(args.variants).split('.')[0]

    library = library_id_to_library_obj(library_id)

    store_library(session, library)

    filters = {
        'min_freq_threshold': args.min_freq_threshold,
        'freq_threshold': args.freq_threshold,
        'min_depth': args.min_depth,
    }

    variants = parse_variants_tsv(args.variants, library_id, filters)

    store_variants(session, variants)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('variants')
    parser.add_argument('--db')
    parser.add_argument('--min-freq-threshold', default=0.25, type=float)
    parser.add_argument('--freq-threshold', default=0.75, type=float)
    parser.add_argument('--min-depth', default=10, type=int)
    args = parser.parse_args()
    main(args)
