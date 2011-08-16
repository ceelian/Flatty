from setuptools import setup, find_packages
from distutils.cmd import Command
import codecs
import sys, os
import doctest
from glob import glob

sys.path.insert(0,'src/')
init_pyc = 'src/flatty/__init__.pyc'
if os.path.exists(init_pyc):
    os.remove(init_pyc)

import flatty


if os.path.exists("doc/source/introduction.rst"):
    long_description = codecs.open('doc/source/introduction.rst', "r", "utf-8").read()
else:
    long_description = "See " + flatty.__homepage__


setuptools_options = {
	'test_suite': 'flatty.tests.suite',
	'zip_safe': True,
}

setup(
    name = "flatty",
    version = flatty.__version__,
    packages = find_packages('src'),
    package_dir = {'':'src'},
  
    # metadata for upload to PyPI
    author = flatty.__author__,
    author_email = flatty.__contact__,
    description = flatty.__doc__,
    long_description=long_description,
    keywords = "marshaller schema objectmapper couchdb mongodb orm",
    platforms=["any"],
    url = flatty.__homepage__,
    license = 'BSD',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    **setuptools_options

 

)

