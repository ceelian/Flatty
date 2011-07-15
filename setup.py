from setuptools import setup, find_packages
import codecs
import sys, os
sys.path.insert(0,'src/')
init_pyc = 'src/flatty/__init__.pyc'
if os.path.exists(init_pyc):
    os.remove(init_pyc)

import flatty


if os.path.exists("doc/source/introduction.rst"):
    long_description = codecs.open('doc/source/introduction.rst', "r", "utf-8").read()
else:
    long_description = "See " + flatty.__homepage__

setup(
    name = "flatty",
    version = flatty.__version__,
    packages = find_packages('src'),
    package_dir = {'':'src'},
    #install_requires = ['couchdb-python>=0.8'],
  
    
    # metadata for upload to PyPI
    author = flatty.__author__,
    author_email = flatty.__contact__,
    description = flatty.__doc__,
    long_description=long_description,
    keywords = "rpc amqp",
    platforms=["any"],
    url = flatty.__homepage__,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Intended Audience :: Developers",
        "Topic :: Communications",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
 

)

