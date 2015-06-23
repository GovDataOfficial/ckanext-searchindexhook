=============
ckanext-searchindexhook
=============

This extension adds package data to the search index or deletes package data from the
search index by hooking into the ``IPackageController`` interface methods ``before_index``
(for additions) and ``after_delete`` (for deletions).

------------
Requirements
------------

This extension requires at least a CKAN 2.1.* version plus an installation of the govdatade
CKAN extension when it's also required to add harvested data to the search index.

------------
Installation
------------

To install ckanext-searchindexhook:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-searchindexhook Python package into your virtual environment::

     pip install ckanext-searchindexhook

3. Add ``searchindexhook`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload

---------------
Config Settings
---------------

To configure the extension add these two configuration settings to your CKAN
config file (by default the config file is located at ``/etc/ckan/default/production.ini``).

# The endpoint of the search index webservice.
ckanext.ckan.searchindexhook.endpoint = http://search-index.sbw.imbw.dev.seitenbau.net:9084

# The HTTP basic auth credentials for the search index webservice.
# Colons are disallowed for usage in the username or password.
ckanext.ckan.searchindexhook.endpoint.credentials = username:password

------------------------
Development Installation
------------------------

To install ckanext-searchindexhook for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/raphaelstolt/ckanext-searchindexhook.git
    cd ckanext-searchindexhook
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.searchindexhook --cover-inclusive --cover-erase --cover-tests


---------------------------------
Registering ckanext-searchindexhook on PyPI
---------------------------------

ckanext-searchindexhook should be availabe on PyPI as
https://pypi.python.org/pypi/ckanext-searchindexhook. If that link doesn't work, then
you can register the project on PyPI for the first time by following these
steps:

1. Create a source distribution of the project::

     python setup.py sdist

2. Register the project::

     python setup.py register

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the first release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.1 then do::

       git tag 0.0.1
       git push --tags


----------------------------------------
Releasing a New Version of ckanext-searchindexhook
----------------------------------------

ckanext-searchindexhook is availabe on PyPI as https://pypi.python.org/pypi/ckanext-searchindexhook.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI::

     python setup.py sdist upload

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
