# ckanext-searchindexhook

This extension adds package data to the search index or deletes package data from the
search index by hooking into the ``IPackageController`` interface methods ``before_index``
(for additions) and ``after_delete`` (for deletions).


Requirements
------------

This extension requires at least a CKAN 2.1.* version plus an installation of the search index services for the used Elasticsearch in [GovData](https://github.com/GovDataOfficial/GovData/).


Installation
------------

To install ckanext-searchindexhook:

1. Activate your CKAN virtual environment, for example::

     . /path/to/virtualenv/bin/activate

2. Install the ckanext-searchindexhook Python package into your virtual environment::

     /path/to/virtualenv/bin/pip install -e git+git://github.com/GovDataOfficial/ckanext-searchindexhook.git#egg=ckanext-searchindexhook

3. Modify the CKAN configuration file

- Add ``search_index_hook`` to the ``ckan.plugins`` parameter in your CKAN
   config file ``/path/to/ckan/config/production.ini``).

- To configure the extension add the following configuration settings

  # The endpoint of the search index webservice.
  ckan.searchindexhook.endpoint = http://localhost:9070/index-queue/

  # The HTTP basic auth credentials for the search index webservice.
  # Colons are disallowed for usage in the username or password, the default is kermit:kermit.
  ckan.searchindexhook.endpoint.credentials = username:password

  # The base path of the target link to which the dataset name is appended
  ckan.searchindexhook.targetlink.url.base.path = /web/guest/suchen/-/details/

  # Name of the search index
  ckan.searchindexhook.index.name = govdata-ckan-de

  # List of comma separated, indexable package / dataset types
  ckan.searchindexhook.indexable.data.types = datensatz,dataset,dokument,app

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


Running the Tests
-----------------

Add the following line to the /path/to/ckan/test-core.ini::

    sqlalchemy.url = postgresql://ckantesting:test@localhost/ckantesting

To run the tests, do::

    cd ckanext-searchindexhook
    nosetests --nologcapture --with-pylons=test.ini ckanext/searchindexhook/tests/*.py

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.searchindexhook --cover-inclusive --cover-erase --cover-tests ckanext/searchindexhook/tests/*.py
