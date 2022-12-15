from codecs import open  # To use a consistent encoding
from os import path

from setuptools import setup, find_packages  # Always prefer setuptools over distutils


VERSION = '5.8.0'
here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open('base-requirements.txt') as f:
    required = [line.strip() for line in f]

setup(
    name='''ckanext-searchindexhook''',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version=VERSION,

    description='''A CKAN extension to add and delete package data from a search index.''',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/GovDataOfficial/ckanext-searchindexhook',

    # Author details
    author='SEITENBAU GmbH',
    author_email='info@seitenbau.com',

    # Choose your license
    license='AGPL',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        # 3 - Alpha
        # 4 - Beta
        # 5 - Production/Stable
        # 6 - Mature
        # 7 - Inactive
        'Development Status :: 4 - Beta',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],


    # What does your project relate to?
    keywords='''CKAN search index govdata''',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    install_requires=required,
    include_package_data=True,
    package_data={
    },
    namespace_packages=['ckanext'],

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points='''
        [ckan.plugins]
        search_index_hook=ckanext.searchindexhook.plugin:SearchIndexHookPlugin
    ''',
)
