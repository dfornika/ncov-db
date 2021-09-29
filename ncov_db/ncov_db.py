#!/usr/bin/env python

import argparse
import sys

import alembic.config

from . import store_sequencing_run
from . import store_melted_freebayes_vcfs
from . import store_pangolin_results

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
        store_sequencing_run.main(args)

    def load_melted_freebayes_vcfs(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--db', required=True)
        parser.add_argument('melted_vcfs_dir')
        args = parser.parse_args(sys.argv[2:])
        kwargs = {
            'db': args.db,
            'melted_vcfs_dir': args.melted_vcfs_dir,
        }
        store_melted_freebayes_vcfs.main(args)

    def load_pangolin_results(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--db', required=True)
        parser.add_argument('pangolin_results')
        args = parser.parse_args(sys.argv[2:])
        kwargs = {
            'db': args.db,
            'pangolin_results': args.pangolin_results,
        }
        store_pangolin_results.main(args)


def main():
    SubCommands()
    

if __name__ == '__main__':
    main()
