#!/usr/bin/env python
'''Setuptools params'''

from setuptools import setup, find_packages

setup(
    name='hedera',
    version='0.0.0',
    description='Implementation of Hedera Multipath Controller',
    author='Ian Walsh, Anh Truong',
    author_email='iwalsh, anhlt92@stanford.edu',
    packages=find_packages(exclude='test'),
    long_description="""\
Insert longer description here.
      """,
      classifiers=[
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Development Status :: 4 - Beta",
          "Intended Audience :: Developers",
          "Topic :: Internet",
      ],
      keywords='networking protocol Internet OpenFlow data center datacenter',
      license='GPL',
      install_requires=[
        'setuptools',
        'networkx'
      ])
