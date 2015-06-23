import ckan.plugins as plugins
import pylons.config as config
import requests
import logging
import json

logger = logging.getLogger(__name__)


class SearchindexhookPlugin(plugins.SingletonPlugin):

    '''
    Plugin for adding and deleting package data from the bmi-govdata search index.
    '''
    plugins.implements(plugins.IPackageController, inherit=True)

    search_index_endpoint = config.get(
        'ckan.searchindexhook.endpoint',
        False
    )

    search_index_credentials = config.get(
        'ckan.searchindexhook.endpoint.credentials',
        False
    )

    # IPackageController

    def assert_searchindex_endpoint_configuration(self, s):
        assert_message = 'Configured endpoint is not a string'
        assert isinstance(s, basestring), assert_message

    def assert_searchindex_credentials_configuration(self, s):
        assert_message = 'Configured credentials are not a string'
        assert isinstance(s, basestring), assert_message
        assert_message = 'Credentials not configured in format username:password'
        assert len(s.split(':')) == 2, assert_message

    def assert_indexqueue_configuration(self):
        self.assert_searchindex_endpoint_configuration(
            self.search_index_endpoint
        )
        self.assert_searchindex_credentials_configuration(
            self.search_index_credentials
        )

    def get_search_index_credentials(self):
        credentials = self.search_index_credentials.split(':')
        return {
            'username': credentials[0],
            'password': credentials[1]
        }

    def before_index(self, pkg_dict):
        logger.info("Syncing before Solr indexing")

        logger.info("Package dict")
        logger.info(pkg_dict)

        self.delete_from_index(pkg_dict['id'])
        self.add_to_index(pkg_dict)

        return pkg_dict

    def add_to_index(self, data_dict):
        self.assert_indexqueue_configuration()

        credentials = self.get_search_index_credentials()
        payload = [{
            'indexName': 'opendataindex',
            'type': 'opendata',
            'version': None,
            'displayName': None,
            'document': {
                'id': data_dict['id'],
                'title': data_dict['title'],
                'sprache': None,
                'preamble': None,
                'sections': [],
                'tags': data_dict['tags'],
                'mandant': 1,
                'metadata': None
            }
        }]

        r = requests.post(
            self.search_index_endpoint + '/index-queue/',
            auth=(credentials['username'], credentials['password']),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )

        logger.info("Adding to index: ")
        logger.info(json.dumps(payload))

        logger.info("Service reponse status code: (code=%d)" % r.status_code)

        r.raise_for_status()

    def delete_from_index(self, document_id):
        self.assert_searchindex_endpoint_configuration(
            self.search_index_endpoint
        )

        credentials = self.get_search_index_credentials()

        payload = [{
            'indexName': 'opendataindex',
            'type': 'opendata',
            'version': None,
            'displayName': None,
            'document': {
                'id': document_id,
                'title': None,
                'sprache': None,
                'preamble': None,
                'sections': [],
                'tags': [],
                'mandant': 1,
                'metadata': None
            }
        }]

        index_queue_url = self.search_index_endpoint + '/index-queue/'

        r = requests.delete(
            index_queue_url + document_id,
            auth=(credentials['username'], credentials['password']),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )

        logger.info("Deleting from index: (id=%s)" % document_id)
        logger.info(json.dumps(payload))
        logger.info("Service reponse status code: (code=%d)" % r.status_code)
        r.raise_for_status()

    def after_delete(self, context, data_dict):
        '''
        Deletes the entity data from the index queue after entity
        deletion.
        '''
        logger.info("Syncing after package deletion")
        self.delete_from_index(data_dict['id'])
