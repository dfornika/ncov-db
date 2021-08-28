from pathlib import Path

from setuptools import setup, find_packages

import ncov_db

setup(
    name='ncov-db',
    version=ncov_db.__version__,
    description='',
    author='Dan Fornika',
    author_email='dan.fornika@bccdc.ca',
    url='',
    packages=find_packages(exclude=('tests', 'tests.*')),
    python_requires='>=3.5',
    install_requires=Path('requirements.txt').read_text(),
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=Path('requirements-tests.txt').read_text(),
    entry_points = {
        'console_scripts': ['ncov-db=ncov_db.ncov_db:main'],
    }
)
