# ncov-db

This tool will pull relevant output data from analysis output directories produced by [BCCDC-PHL/ncov2019-artic-nf](https://github.com/BCCDC-PHL/ncov2019-artic-nf) and [BCCDC-PHL/ncov-tools-nf](https://github.com/BCCDC-PHL/ncov-tools-nf), and load them into a [SQLite](https://www.sqlite.org/index.html) database.

It is designed with our specific analysis output directory structure in mind, so may not be generally applicable to other COVID analysis datasets.

## Installation

ncov-db is pip-installable. It is recommended to create a conda environment or python virtual environment for dependency management.

```
conda create -n ncov-db python=3
conda activate ncov-db
pip install git+https://github.com/dfornika/ncov-db.git
```

## Usage

### Initialize a new database

Before loading any data, a new database must be initialized with the appropriate database schema. This is done using the `ncov-db init` command.
The `ncov-db init` command takes a single argument: the path to the sqlite database file to be created.

```
usage: ncov-db init [-h] --db DB

optional arguments:
  -h, --help  show this help message and exit
  --db DB
```

Example:

```
ncov-db init --db ncov.db
```

### Load data from an analyzed sequencing run into an existing database

Once a database has been initialized, new data can be loaded using the `ncov-db load-run` command. The `ncov-db load-run` command takes two arguments: the path to the analysis directory of the run
to be loaded, and 

```
usage: ncov-db load-run [-h] --db DB run_dir

positional arguments:
  run_dir

optional arguments:
  -h, --help  show this help message and exit
  --db DB
```

