#!/usr/bin/env python

import argparse
import collections
import csv
import json
import os
import sys

from dataclasses import dataclass

import sqlalchemy as sa
import sqlalchemy.orm as sao

from . import models
from .time import now

def library_id_to_container_id(library_id):
    container_id = None
    if not (library_id.startswith('POS') or library_id.startswith('NEG')):
        container_id = library_id.split('-')[0]
    return container_id


def library_id_to_container_obj(library_id):
    container_obj = models.Container()
    container_obj.container_id = library_id_to_container_id(library_id)
    return container_obj

def library_id_to_library_obj(library_id):
    library = {}
    library_id_components = library_id.split('-')

    library['id'] = library_id
    if library_id.startswith('POS'):
        library['container_id'] = None
        library['library_plate_id'] = library_id_components[2]
        library['index_set_id'] = library_id_components[3]
        library['plate_well'] = 'G12'
    elif library_id.startswith('NEG'):
        library['container_id'] = None
        library['library_plate_id'] = library_id_components[2]
        library['index_set_id'] = library_id_components[3]
        library['plate_well'] = 'H12'
    else:
        library['container_id'] = library_id_components[0]
        library['library_plate_id'] = library_id_components[1]
        library['index_set_id'] = library_id_components[2]
        library['plate_well'] = library_id_components[3]
    library['plate_row'] = library['plate_well'][0]
    library['plate_col'] = int(library['plate_well'][-2:])
    
    library_obj = models.Library()
    for key in library.keys():
        setattr(library_obj, key, library[key])

    return library_obj

def parse_variants_tsv(variants_tsv_path, library_id, filters):
    field_name_conversion = {
        'REGION':      'ref_accession',
        'POS':         'nucleotide_position',
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
        'GFF_FEATURE': 'gene_name',
        'REF_CODON':   'ref_codon',
        'REF_AA':      'ref_amino_acid',
        'ALT_CODON':   'alt_codon',
        'ALT_AA':      'alt_amino_acid',
        'CODON_POS':   'codon_position',
        'MUT_NAME':    'mutation_name_by_amino_acid',
    }

    int_fields = [
        'nucleotide_position',
        'ref_allele_depth',
        'ref_allele_depth_reverse_reads',
        'ref_allele_mean_quality',
        'alt_allele_depth',
        'alt_allele_depth_reverse_reads',
        'alt_allele_mean_quality',
        'total_depth',
        'codon_position',
    ]

    float_fields = [
        'alt_allele_frequency',
        'p_value_fishers_exact',
    ]

    bool_fields = [
        'p_value_pass',
    ]

    na_null_fields = [
        'gene_name',
        'ref_codon',
        'ref_amino_acid',
        'alt_codon',
        'alt_amino_acid',
        'codon_position',
        'mutation_name_by_amino_acid',
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
                if k in row:
                    variant[v] = row[k]
                else:
                    variant[v] = None

            for f in na_null_fields:
                if variant[f] == 'NA':
                    variant[f] = None

            for f in int_fields:
                if variant[f] is not None:
                    variant[f] = int(variant[f])

            for f in float_fields:
                if variant[f] is not None:
                    variant[f] = float(variant[f])

            for f in bool_fields:
                if variant[f] is not None:
                    variant[f] = bool(variant[f])
            

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
                    log_msg = collections.OrderedDict()
                    log_msg['timestamp'] = now()
                    log_msg['event_type'] = 'loading_error'
                    log_msg['input_file'] = os.path.abspath(variants_tsv_path)
                    log_msg['input_data_details'] = {
                        'library_id': variant['library_id'],
                        'nucleotide_position': str(variant['nucleotide_position']),
                        'ref_allele': variant['ref_allele'],
                        'alt_allele': variant['alt_allele'],
                        'alt_allele_frequency': str(variant['alt_allele_frequency']),
                    }
                    print(json.dumps(log_msg))

            if variant['variant_type'] == 'snp':
                try:
                    if variant['consensus_allele'] in {'M', 'R', 'W', 'S', 'Y', 'K'}:
                        variant['is_ambiguous'] = True
                    else:
                        variant['is_ambiguous'] = False
                except KeyError as e:
                    log_msg = collections.OrderedDict()
                    log_msg['timestamp'] = now()
                    log_msg['event_type'] = 'loading_error'
                    log_msg['input_file'] = os.path.abspath(variants_tsv_path)
                    log_msg['input_data_details'] = {
                        'library_id': variant['library_id'],
                        'nucleotide_position': str(variant['nucleotide_position']),
                        'ref_allele': variant['ref_allele'],
                        'alt_allele': variant['alt_allele'],
                        'alt_allele_frequency': str(variant['alt_allele_frequency']),
                    }
                    print(json.dumps(log_msg))

            variant_obj = models.VariantIvar()
            for key in variant.keys():
                setattr(variant_obj, key, variant[key])

            variants.append(variant_obj)

    return variants


def store_container_for_library(session, library):
    container_id = library.id.split('-')[0]
    
    existing_container = (
        session.query(models.Container)
        .filter(
            models.Container.id == container_id
        )
        .one_or_none()
    )

    if existing_container is None:
        container = models.Container()
        container.id = container_id
        session.add(container)
        session.commit()

    return None


def store_library(session, library):
    if not (library.id.startswith('POS') or library.id.startswith('NEG')):
        store_container_for_library(session, library)
    
    existing_library = (
        session.query(models.Library)
        .filter(
            models.Library.id == library.id
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
            session.query(models.VariantIvar)
            .filter(
                sa.and_(
                    models.VariantIvar.library_id == variant.library_id,
                    models.VariantIvar.variant_calling_tool == variant.variant_calling_tool,
                    models.VariantIvar.variant_calling_tool_version == variant.variant_calling_tool_version,
                    models.VariantIvar.ref_accession == variant.ref_accession,
                    models.VariantIvar.nucleotide_position == variant.nucleotide_position,
                    models.VariantIvar.ref_allele == variant.ref_allele,
                    models.VariantIvar.alt_allele == variant.alt_allele,
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
    

def main(args, kwargs=None):
    if not args:    
        args = Args(**kwargs)

    connection_string = "sqlite+pysqlite:///" + args.db
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


@dataclass
class Args:
    db: str
    variants: str
    min_freq_threshold: float = 0.25
    freq_threshold: float = 0.75
    min_depth: int = 10

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('variants')
    parser.add_argument('--db', required=True)
    parser.add_argument('--min-freq-threshold', default=0.25, type=float)
    parser.add_argument('--freq-threshold', default=0.75, type=float)
    parser.add_argument('--min-depth', default=10, type=int)
    args = parser.parse_args()
    main(args)
