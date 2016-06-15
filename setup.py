#!/usr/bin/env python

# Script information for the file.
__author__ = "Hendrix Demers (hendrix.demers@mail.mcgill.ca)"
__version__ = "0.1"
__date__ = "Jun 15, 2016"
__copyright__ = "Copyright (c) 2016 Hendrix Demers"
__license__ = "Apache License Version 2.0"

# Standard library modules.
import os
import zipfile
from distutils.cmd import Command

# Third party modules.
from setuptools import setup, find_packages
import py2exe

# Local modules.

# Globals and constants variables.

class TestDataCommand(Command):

    description = "create a zip of all files in the testData folder"
    user_options = [('dist-dir=', 'd',
                     "directory to put final built distributions in "
                     "[default: dist]"), ]

    def initialize_options(self):
        self.dist_dir = None

    def finalize_options(self):
        if self.dist_dir is None:
            self.dist_dir = "dist"

    def run(self):
        if not os.path.isdir(self.dist_dir):
            os.makedirs(self.dist_dir)

        basepath = os.path.dirname(__file__)
        testdatapath = os.path.join(basepath, 'testData')

        zipfilename = self.distribution.get_fullname() + '-testData.zip'
        zipfilepath = os.path.join(self.dist_dir, zipfilename)
        with zipfile.ZipFile(zipfilepath, 'w') as z:
            for root, _dirs, files in os.walk(testdatapath):
                for file in files:
                    filename = os.path.join(root, file)
                    arcname = os.path.relpath(filename, basepath)
                    z.write(filename, arcname)

setup(name="pyCrossCourt",
      version='0.1',
      url='https://github.com/drix00/pycrosscourt',
      description="Python script to help the preparation of the input data for CrossCourt and the analysis of the CrossCourt results.",
      author="Hendrix Demers",
      author_email="hendrix.demers@mail.mcgill.ca",
      license="ALv2",
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: Apache License Version 2.0  (ALv2)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Operating System :: OS Independent',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Scientific/Engineering :: Physics'],

      packages=find_packages(),

      include_package_data=False, # Do not include test data

      install_requires=['Pillow'],
      setup_requires=['nose', 'coverage'],

      test_suite='nose.collector',

      cmdclass={'zip_testdata': TestDataCommand},

      console=['pycrosscourt/main_gui.py'],
)
