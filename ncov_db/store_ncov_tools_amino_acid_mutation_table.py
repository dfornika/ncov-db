#!/usr/bin/env python

import argparse
import collections
import csv
import json
import os
import re
import sys

from dataclasses import dataclass
from datetime import date

import sqlalchemy as sa
import sqlalchemy.orm as sao

import ncov_db.model as model


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


def parse_amino_acid_mutation_tsv(amino_acid_mutation_tsv_path):

    field_translation = {
        'sample': 'library_id',
        'chr': 'ref_accession',
        'pos': 'nucleotide_position',
        'ref': 'ref_allele',
        'alt': 'alt_allele',
        'Consequence': 'consequence',
        'gene': 'gene',
        'protein': 'amino_acid_change',
        'aa': 'mutation_name_by_amino_acid',
    }

    int_fields = [
        'nucleotide_position',
    ]

    na_null_fields = [
        'mutation_name_by_amino_acid',
    ]

    empty_null_fields = [
        'amino_acid_change',
    ]

    aa_mutations = []

    with open(amino_acid_mutation_tsv_path, 'r', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            m = collections.OrderedDict()
            for k, v in field_translation.items():
                m[v] = row[k]

            for f in int_fields:
                m[f] = int(m[f])

            for f in na_null_fields:
                if m[f] == 'NA':
                    m[f] = None

            for f in empty_null_fields:
                if m[f] == '':
                    m[f] = None

            if m['amino_acid_change'] and not re.search('deletion', m['consequence']):
                ref_aa_match = re.search('^[A-Z]+', m['amino_acid_change'])
                if ref_aa_match:
                    m['ref_amino_acid'] = ref_aa_match.group(0)
                else:
                    m['ref_amino_acid'] = None
                codon_position_match = re.search('[0-9]+', m['amino_acid_change'])
                if codon_position_match:
                    m['codon_position'] = int(codon_position_match.group(0))
                else:
                    m['codon_position'] = None
                alt_aa_match = re.search('[A-Z]+$', m['amino_acid_change'])
                if alt_aa_match:
                    m['alt_amino_acid'] = alt_aa_match.group(0)
                else:
                    m['alt_amino_acid'] = None
            else:
                m['ref_amino_acid'] = None
                m['codon_position'] = None
                m['alt_amino_acid'] = None

            m.pop('amino_acid_change')

            if m['gene'] is not None:
                m['gene'] = m['gene'].replace('orf', 'ORF')

            if m['mutation_name_by_amino_acid'] is not None:
                m['mutation_name_by_amino_acid'] = m['mutation_name_by_amino_acid'].replace('-', ':').replace('orf', 'ORF')
            
            aa_mutation_obj = model.NcovToolsAminoAcidMutation()
            for key in m.keys():
                setattr(aa_mutation_obj, key, m[key])
                aa_mutations.append(aa_mutation_obj)

    return aa_mutations


def store_amino_acid_mutations(session, amino_acid_mutations):
    for idx, amino_acid_mutation in enumerate(amino_acid_mutations):
        container_id = library_id_to_container_id(amino_acid_mutation.library_id)
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
                new_container = library_id_to_container_obj(amino_acid_mutation.library_id)
                session.add(new_container)
                session.commit()
    
        existing_library = (
            session.query(model.Library)
            .filter(
                sa.and_(
                    model.Library.library_id == amino_acid_mutation.library_id
                )
            )
            .one_or_none()
        )

        if existing_library is None:
            new_library = library_id_to_library_obj(amino_acid_mutation.library_id)
            session.add(new_library)
            session.commit()

        existing_amino_acid_mutation = (
            session.query(model.NcovToolsAminoAcidMutation)
            .filter(
                sa.and_(
                    model.NcovToolsAminoAcidMutation.library_id == amino_acid_mutation.library_id,
                    model.NcovToolsAminoAcidMutation.ref_accession == amino_acid_mutation.ref_accession,
                    model.NcovToolsAminoAcidMutation.nucleotide_position == amino_acid_mutation.nucleotide_position,
                    model.NcovToolsAminoAcidMutation.ref_allele == amino_acid_mutation.ref_allele,
                    model.NcovToolsAminoAcidMutation.alt_allele == amino_acid_mutation.alt_allele,
                )
            )
            .one_or_none()
        )
    
        if existing_amino_acid_mutation is None:
            session.add(amino_acid_mutation)
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

    aa_mutations = parse_amino_acid_mutation_tsv(args.ncov_tools_aa_table)

    
    store_amino_acid_mutations(session, aa_mutations)


@dataclass
class Args:
    db: str
    ncov_tools_aa_table: str

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ncov_tools_aa_table')
    parser.add_argument('--db', required=True)
    args = parser.parse_args()
    main(args)
