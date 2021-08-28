#!/usr/bin/env python

import argparse
import sys

import alembic.config

import ncov_db.store_sequencing_run

'''
There are more sophisticated libraries for building sub-commands but
the structure of this file is based on this guide for doing it with argparse:
https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
'''

class SubCommands(object):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        subcommand_fn = args.command.replace('-', '_')
        if not hasattr(self, subcommand_fn):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, subcommand_fn)()

    def init(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--db', required=True)
        args = parser.parse_args(sys.argv[2:])
        alembic_args = [
            '--raiseerr',
            '-x',
            'db=sqlite:///' + args.db,
            'upgrade',
            'head',
        ]
        alembic.config.main(argv=alembic_args)

    def load_run(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--db', required=True)
        parser.add_argument('run_dir')
        args = parser.parse_args(sys.argv[2:])
        kwargs = {
            'db': args.db,
            'run_dir': args.run_dir,
        }
        ncov_db.store_sequencing_run.main(args)


def main():
    SubCommands()
    

if __name__ == '__main__':
    main()
