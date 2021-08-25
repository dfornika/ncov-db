#!/usr/bin/env python

import argparse
import collections
import csv
import json
import os
import sys

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class IvarVariant(Base):
    __tablename__ = "variant_ivar"
    library_id                     = Column(String, primary_key=True)
    variant_calling_tool           = Column(String, primary_key=True)
    variant_calling_tool_version   = Column(String, primary_key=True)
    ref_accession                  = Column(String, primary_key=True)
    position                       = Column(Integer, primary_key=True)
    ref_allele                     = Column(String, primary_key=True)
    alt_allele                     = Column(String, primary_key=True)
    ref_allele_depth               = Column(Integer)
    ref_allele_depth_reverse_reads = Column(Integer)
    ref_allele_mean_quality        = Column(Integer)
    alt_allele_depth               = Column(Integer)
    alt_allele_depth_reverse_reads = Column(Integer)
    alt_allele_mean_quality        = Column(Integer)
    alt_allele_frequency           = Column(Float)
    consensus_allele               = Column(String)
    variant_type                   = Column(String)
    is_ambiguous                   = Column(Boolean)
    total_depth                    = Column(Integer)
    p_value_fishers_exact          = Column(Float)
    p_value_pass                   = Column(Boolean)
    gff_feature                    = Column(String)
    ref_codon                      = Column(String)
    ref_amino_acid                 = Column(String)
    alt_codon                      = Column(String)
    alt_amino_acid                 = Column(String)

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

            variant_obj = IvarVariant()
            for key in variant.keys():
                setattr(variant_obj, key, variant[key])

            variants.append(variant_obj)

    return variants


def store_variant(session, variant):
    session.add(variant)
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
    
    library_id = os.path.basename(args.variants).split('.')[0]

    filters = {
        'min_freq_threshold': args.min_freq_threshold,
        'freq_threshold': args.freq_threshold,
        'min_depth': args.min_depth,
    }

    variants = parse_variants_tsv(args.variants, library_id, filters)

    for variant in variants:
        store_variant(session, variant)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('variants')
    parser.add_argument('--db')
    parser.add_argument('--min-freq-threshold', default=0.25, type=float)
    parser.add_argument('--freq-threshold', default=0.75, type=float)
    parser.add_argument('--min-depth', default=10, type=int)
    args = parser.parse_args()
    main(args)
