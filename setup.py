#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path
import sys

pkg_name = 'workflow_miniscope'
here = path.abspath(path.dirname(__file__))

long_description = """"
# Workflow for miniscope calcium imaging data acquired with Miniscope-DAQ-V3 software and analyzed with MiniscopeAnalysis.

Build a complete imaging workflow using the DataJoint elements
+ [elements-lab](https://github.com/datajoint/elements-lab)
+ [elements-animal](https://github.com/datajoint/elements-animal)
+ [element-miniscope](https://github.com/datajoint/element-miniscope)
"""

with open(path.join(here, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

with open(path.join(here, pkg_name, 'version.py')) as f:
    exec(f.read())

setup(
    name='workflow-miniscope',
    version=__version__,
    description="Miniscope calcium imaging workflow using the DataJoint elements",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='DataJoint NEURO',
    author_email='info@vathes.com',
    license='MIT',
    url='https://github.com/datajoint/workflow-miniscope',
    keywords='neuroscience datajoint calcium-imaging miniscope',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=requirements,
)
