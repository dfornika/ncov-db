from pathlib import Path

from setuptools import setup, find_packages

import store_variants

setup(
    name='store_variants',
    version=store_variants.__version__,
    description='',
    author='Dan Fornika',
    author_email='dan.fornika@bccdc.ca',
    url='',
    packages=find_packages(exclude=('tests', 'tests.*')),
    python_requires='>=3.5',
    install_requires=Path('requirements.txt').read_text(),
    setup_requires=['pytest-runner', 'flake8'],
    tests_require=Path('requirements-tests.txt').read_text(), 
)
