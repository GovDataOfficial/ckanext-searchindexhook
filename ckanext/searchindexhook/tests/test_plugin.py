# -*- coding: utf-8 -*-
'''
Tests for the ckanext.searchindexhook extension.
'''
import datetime
import pylons.config as config
import webtest
import unittest
import ckan.model as model
import ckan.plugins
import json
import geojson

from nose.tools import assert_raises
from mock import Mock, patch, ANY
from requests.exceptions import HTTPError, ConnectionError
from ckanext.searchindexhook.plugin import NORMALIZED_DATE_FORMAT


class TestPlugin(unittest.TestCase, object):
    def setup(self):
        self.app = ckan.config.middleware.make_app(
            config['global_conf'],
            **config
        )
        self.app = webtest.TestApp(self.app)

    def teardown(self):
        ckan.plugins.unload('search_index_hook')
        del config['ckan.searchindexhook.endpoint']
        del config['ckan.searchindexhook.endpoint.credentials']
        del config['ckan.searchindexhook.targetlink.url.base.path']
        del config['ckan.searchindexhook.index.name']
        model.repo.rebuild_db()

    def test_assert_credentials_configuration_raises_expected_error(self):
        plugin = self.get_plugin_instance()
        assert_raises(
            AssertionError,
            plugin.assert_credentials_configuration,
            None
        )

    def test_assert_credentials_configuration_raises_no_error(self):
        plugin = self.get_plugin_instance()
        self.assertEquals(
            None,
            plugin.assert_credentials_configuration('abc:123')
        )

    def test_assert_endpoint_configuration_raises_expected_error(self):
        plugin = self.get_plugin_instance()
        assert_raises(
            AssertionError,
            plugin.assert_endpoint_configuration,
            None
        )

    def test_assert_endpoint_configuration_raises_no_error(self):
        plugin = self.get_plugin_instance()
        self.assertEquals(
            None,
            plugin.assert_endpoint_configuration('abc')
        )

    def test_assert_credentials_configuration_raises_expected_error(self):
        plugin = self.get_plugin_instance()
        assert_raises(
            AssertionError,
            plugin.assert_credentials_configuration,
            None
        )

    def test_assert_configuration_raises_expected_error_for_missing_endpoint(self):
        plugin = self.get_plugin_instance()
        plugin.search_index_endpoint = None
        assert_raises(
            AssertionError,
            plugin.assert_configuration
        )

    def test_assert_configuration_raises_expected_error_for_missing_credentials(self):
        plugin = self.get_plugin_instance()
        plugin.search_index_credentials = None
        plugin.search_index_endpoint = 'http://test.endpoint'
        assert_raises(
            AssertionError,
            plugin.assert_configuration
        )

    def test_assert_configuration_raises_expected_error_for_no_colon_credentials(self):
        plugin = self.get_plugin_instance()
        plugin.search_index_credentials = 'testuser-testpassword'
        assert_raises(
            AssertionError,
            plugin.assert_configuration
        )

    def test_assert_mandatory_dict_keys_raises_no_error(self):
        plugin = self.get_plugin_instance()

        extras_dict = {
            "key": "value"
        }

        resources_dict = {
            "resources": [{
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
            }],
            "extras": extras_dict
        }

        data_dict = {
            'data_dict': json.dumps(resources_dict)
        }

        self.assertEquals(
            None,
            plugin.assert_mandatory_dict_keys(data_dict)
        )

    def test_assert_mandatory_dict_keys_raises_error_for_missing_data_dict_key(self):
        plugin = self.get_plugin_instance()

        data_dict = {
            'key': 'value'
        }

        assert_raises(
            AssertionError,
            plugin.assert_mandatory_dict_keys,
            data_dict
        )

    def test_assert_mandatory_dict_keys_raises_error_for_missing_resources_key(self):
        plugin = self.get_plugin_instance()

        things_dict = {
            "things": {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
            }
        }

        data_dict = {
            'data_dict': json.dumps(things_dict)
        }

        assert_raises(
            AssertionError,
            plugin.assert_mandatory_dict_keys,
            data_dict
        )

    def test_assert_mandatory_dict_keys_raises_error_for_missing_extras_key(self):
        plugin = self.get_plugin_instance()

        special_dict = {
            "key": "value"
        }

        resources_dict = {
            "resources": [{
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
            }],
            "special": special_dict
        }

        data_dict = {
            'data_dict': json.dumps(resources_dict)
        }

        assert_raises(
            AssertionError,
            plugin.assert_mandatory_dict_keys,
            data_dict
        )

    def test_should_be_indexed_works_for_indexable_dataset_type(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'test'

        self.assertTrue(plugin.should_be_indexed('test'))
        self.assertTrue(plugin.should_be_indexed('test   '))

    def test_should_be_indexed_works_for_non_indexable_dataset_type(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'test'

        self.assertFalse(plugin.should_be_indexed('boo'))
        self.assertFalse(plugin.should_be_indexed('yaa'))

    def test_get_indexable_data_types(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'one,two, three,                         four'

        self.assertEquals(
            type(plugin.get_indexable_data_types()).__name__,
            'list'
        )
        self.assertTrue(len(plugin.get_indexable_data_types()) == 4)
        self.assertTrue('one' in plugin.get_indexable_data_types())
        self.assertTrue('two' in plugin.get_indexable_data_types())
        self.assertTrue('three' in plugin.get_indexable_data_types())
        self.assertTrue('four' in plugin.get_indexable_data_types())

    def test_get_credentials_has_expected_keys(self):
        plugin = self.get_plugin_instance()
        plugin.search_index_credentials = 'testuser:testpassword'
        self.assertTrue(len(plugin.get_search_index_credentials()) == 2)
        self.assertTrue('username' in plugin.get_search_index_credentials())
        self.assertTrue('password' in plugin.get_search_index_credentials())

    def test_assert_configuration_raises_expected_error_for_missing_targetlink_url_base_path(self):
        plugin = self.get_plugin_instance()
        plugin.search_index_credentials = 'testuser:testpassword'
        plugin.search_index_endpoint = 'http://test.endpoint'
        plugin.targetlink_url_base_path = None

        assert_raises(
            AssertionError,
            plugin.assert_configuration
        )

    def test_assert_configuration_raises_expected_error_for_missing_index_name(self):
        plugin = self.get_plugin_instance()
        plugin.search_index_credentials = 'testuser:testpassword'
        plugin.search_index_endpoint = 'http://test.endpoint'
        plugin.targetlink_url_base_path = '/foo/bar/'
        plugin.search_index_name = None
        assert_raises(
            AssertionError,
            plugin.assert_configuration
        )

    def test_get_targetlink_url_base_path_completes_path(self):
        plugin = self.get_plugin_instance()
        plugin.targetlink_url_base_path = 'foooo/bar'
        self.assertEquals(
            plugin.targetlink_url_base_path + '/',
            plugin.get_targetlink_url_base_path()
        )

    def test_get_targetlink_url_base_path_returns_path_as_is_when_closing_slash_is_set(self):
        plugin = self.get_plugin_instance()
        plugin.targetlink_url_base_path = 'test/path/'
        self.assertEquals(
            plugin.targetlink_url_base_path,
            plugin.get_targetlink_url_base_path()
        )

    def test_get_endpoint_completes_path(self):
        plugin = self.get_plugin_instance()
        plugin.search_index_endpoint = 'http://www.ws.de/test'
        self.assertEquals(
            plugin.search_index_endpoint + '/',
            plugin.get_search_index_endpoint()
        )

    def test_get_endpoint_returns_path_as_is_when_closing_slash_is_set(self):
        plugin = self.get_plugin_instance()
        plugin.search_index_endpoint = 'http://www.ws.de/test/'
        self.assertEquals(
            plugin.search_index_endpoint,
            plugin.get_search_index_endpoint()
        )

    def test_substitute_targetlink_works_as_expected(self):
        plugin = self.get_plugin_instance()
        plugin.targetlink_url_base_path = '/test/path/'
        dataset_name = 'example-dataset'
        substituted_targetlink = plugin.substitute_targetlink(dataset_name)
        self.assertEquals(
            plugin.targetlink_url_base_path + dataset_name,
            substituted_targetlink
        )

    def test_after_delete_gets_delegated(self):
        plugin = self.get_plugin_instance()
        pre_mock_def = plugin.delete_from_index
        plugin.delete_from_index = Mock()

        context = None
        data_dict = {'id': 15}

        plugin.after_delete(context=context, data_dict=data_dict)
        plugin.delete_from_index.assert_called_once_with(
            data_dict['id'],
            context
        )

        plugin.delete_from_index = pre_mock_def

    def test_before_index_deletes_and_adds(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'indexable_dataset'

        pre_mock_def = plugin.delete_from_index
        plugin.delete_from_index = Mock()
        plugin.add_to_index = Mock()

        pkg_dict = {'id': 15, 'name': 'package-1', 'type': 'indexable_dataset'}

        plugin.before_index(pkg_dict)
        plugin.delete_from_index.assert_called_once_with(pkg_dict['id'])
        plugin.add_to_index.assert_called_once_with(pkg_dict)

        plugin.delete_from_index = pre_mock_def

    def test_before_index_not_touched_for_non_indexable_dataset(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'indexable_dataset'

        pre_mock_def = plugin.delete_from_index
        plugin.delete_from_index = Mock()
        plugin.add_to_index = Mock()

        pkg_dict = {
            'id': 15, 'name': 'package-1', 'type': 'non_indexable_dataset'
        }

        plugin.before_index(pkg_dict)
        assert not plugin.delete_from_index.called, 'delete_from_index was called and should not have been'
        assert not plugin.add_to_index.called, 'add_to_index was called and should not have been'

        plugin.delete_from_index = pre_mock_def

    def test_before_index_not_touched_for_non_set_dataset_type(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'indexable_dataset'

        pre_mock_def = plugin.delete_from_index
        plugin.delete_from_index = Mock()
        plugin.add_to_index = Mock()

        pkg_dict = {
            'id': 15, 'name': 'package-1'
        }

        plugin.before_index(pkg_dict)
        assert not plugin.delete_from_index.called, 'delete_from_index was called and should not have been'
        assert not plugin.add_to_index.called, 'add_to_index was called and should not have been'

        plugin.delete_from_index = pre_mock_def

    def _build_pkg_dict(self, data_dict):
        return {
            'id': 15, 'type': 'test-type',
            'private': False,
            'title': 'test-title', 'notes': 'test-notes',
            'tags': 'test-tags', 'name': 'test-name',
            'author': 'Paul Test',
            'author_email': 'paul.test@testing.org',
            'maintainer': 'Paul Maintain',
            'maintainer_email': 'paul.maintain@maintaining.org',
            'groups': ['group-one', 'group-two'],
            'type': 'indexable_dataset',
            'notes': 'Some test note',
            'license_id': 'MIT',
            'state': 'active',
            'metadata_created': '2015-08-24T11:19:57.586631',
            'metadata_modified': '2015-08-24T11:19:57.606949',
            'name': 'test-name',
            'isopen': True,
            'owner_org': 'ownerOrg',
            'data_dict': json.dumps(data_dict)
        }

    def _build_metadata_dict(self, pkg_dict, data_dict):
        return {
            'state': pkg_dict['state'],
            'private': pkg_dict['private'],
            'name': pkg_dict['name'],
            'author': pkg_dict['author'],
            'author_email': pkg_dict['author_email'],
            'maintainer': pkg_dict['maintainer'],
            'maintainer_email': pkg_dict['maintainer_email'],
            'groups': pkg_dict['groups'],
            'notes': pkg_dict['notes'],

            # license information from resources, in this case: "testResLicense" is an open license.
            "has_open": False,
            "has_closed": False,
            "resources_licenses": [],

            # Quality metrics: set to false as default
            "has_access_url": False,
            "has_formats": False,

            'metadata_created': pkg_dict['metadata_created'],
            'metadata_modified': pkg_dict['metadata_modified'],
            'dct_modified_fallback_ckan': pkg_dict['metadata_modified'],  # default value
            'type': pkg_dict['type'],
            'owner_org': pkg_dict['owner_org'],
            'resources': data_dict['resources'],
            'extras': data_dict['extras']
        }

    def _build_expected_payload(self, pkg_dict, metadata_dict, plugin):
        return [{
            'indexName': plugin.search_index_name,
            'type': pkg_dict['type'],
            'version': None,
            'displayName': None,
            'document': {
                'id': pkg_dict['id'],
                'title': pkg_dict['title'],
                'preamble': pkg_dict['notes'],
                'sprache': None,
                'sections': [],
                'tags': pkg_dict['tags'],
                'mandant': 1,
                'metadata': json.dumps(metadata_dict),
                'targetlink': plugin.substitute_targetlink(pkg_dict['name'])
            }
        }]

    def _build_plugin_add_index(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'indexable_dataset'
        plugin.search_index_endpoint = 'http://www.ws.de/test/'
        plugin.search_index_credentials = 'testuser:testpassword'
        plugin.targetlink_url_base_path = '/test/path/'
        plugin.search_index_name = 'test-index'
        return plugin

    def _check_payload(self, expected_payload, request_mock):
        '''
        Checks if the mock was called with a data parameter which contains the same
        values as expected_payload.
        This ignores the order of the dict items.
        '''
        # unset output diff limit for dict comparisons.
        self.maxDiff = None

        args, kwargs = request_mock.call_args
        json_raw = kwargs['data']
        actual_payload = json.loads(json_raw)
        # Payload is a list of dicts, and we use only one document
        self.assertEquals(1, len(expected_payload),
                          'Invalid expected_payload: Only one dict is supported')
        self.assertEquals(1, len(actual_payload))
        # dump and load again expected data to get unicode strings everywhere
        expected_utf = json.loads(json.dumps(expected_payload))
        # extract the dataset and unserialize all strings to allow a dict comparison
        expected_data = expected_utf[0]
        actual_data = actual_payload[0]

        if expected_data['document']['metadata'] != None:
            self.assertNotEquals(actual_data['document']['metadata'], None)
            expected_meta = json.loads(expected_data['document']['metadata'])
            actual_meta = json.loads(actual_data['document']['metadata'])
            # although this is implicitly checked again below, check it here already as no further
            # checks are needed if the metadata differs
            self.assertDictEqual(expected_meta, actual_meta)

            # write back unserialized metadata to allow comparing all other items
            expected_data['document']['metadata'] = expected_meta
            actual_data['document']['metadata'] = actual_meta

        self.assertDictEqual(expected_data, actual_data)

    @patch('ckanext.searchindexhook.plugin.requests.post')
    def test_add_to_index_works_as_expected(self, mock_post):
        plugin = self._build_plugin_add_index()

        data_dict = {
            "resources": [{
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "license": "testResLicense",
                "access_url": "http://example.com/",
                "format": "csv"
            }, { # second resource without license or urls to check if has_... attributes are built correctly
                "cache_last_updated": None,
                "package_id": "g73d8b97-e6cb-46bf-bbf6-670155f9fbb4"
            }],
            "extras": [{
                "key": "value"
            }]
        }

        pkg_dict = self._build_pkg_dict(data_dict)

        # Set openness map
        plugin.license_openness_map = {"testResLicense": True}

        plugin.add_to_index(pkg_dict)

        metadata_dict = self._build_metadata_dict(pkg_dict, data_dict)
        metadata_dict["resources_licenses"] = ["testResLicense"]
        # One dataset is sufficient for these attributes, so check if they are true
        metadata_dict["has_open"] = True
        metadata_dict["has_formats"] = True
        metadata_dict["has_access_url"] = True

        expected_payload = self._build_expected_payload(pkg_dict, metadata_dict, plugin)

        mock_post.assert_called_once_with(
            plugin.get_search_index_endpoint(),
            auth=('testuser', 'testpassword'),
            headers={'Content-Type': 'application/json'},
            data=ANY
        )
        self._check_payload(expected_payload, mock_post)

    @patch('ckanext.searchindexhook.plugin.requests.post')
    def test_add_to_index_extra_values(self, mock_post):
        plugin = self._build_plugin_add_index()

        data_dict = {
            "resources": [{
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4"
            }],
            "extras": [{
                "key": "temporal_start",
                "value": "2017-08-24T11:19:57+02:00"
            }, {
                "key": "temporal_end",
                "value": "2017-08-30T11:19:57+0200"
            }, {
                "key": "issued",
                "value": "2017-09-01T11:19:57"
            }, {
                "key": "modified",
                "value": "2017-09-02T11:19:57"
            }, {
                "key": "contact_name",
                "value": "Example"
            }, {
                "key": "contact_email",
                "value": "contact@example.com"
            }, {
                "key": "maintainer_tel",
                "value": "tel:+4912345"
            }, {
                "key": "publisher_name",
                "value": "Publisher"
            }, {
                "key": "geocodingText",
                "value": "[\"Hamburg\"]" # values are lists but stored as strings
            }, {
                "key": "politicalGeocodingLevelURI",
                "value": "http://dcat-ap.de/def/politicalGeocoding/Level/state"
            }, {
                "key": "politicalGeocodingURI",
                "value": "[\"http://dcat-ap.de/def/politicalGeocoding/stateKey/02\"]"
            }]
        }

        pkg_dict = self._build_pkg_dict(data_dict)

        plugin.add_to_index(pkg_dict)

        metadata_dict = self._build_metadata_dict(pkg_dict, data_dict)
        metadata_dict['temporal_start'] = "2017-08-24 11:19:57"
        metadata_dict['temporal_end'] = "2017-08-30 11:19:57"
        metadata_dict['dct_issued'] = "2017-09-01 11:19:57"
        metadata_dict['dct_modified'] = "2017-09-02 11:19:57"
        # has to be the same, as dct_modified is set
        metadata_dict['dct_modified_fallback_ckan'] = metadata_dict['dct_modified']
        # contact details should be added as well
        metadata_dict['contact_name'] = "Example"
        metadata_dict['contact_email'] = "contact@example.com"
        metadata_dict['maintainer_tel'] = "tel:+4912345"
        metadata_dict['publisher_name'] = "Publisher"
        # geocoding
        metadata_dict['geocodingText'] = "[\"Hamburg\"]"
        metadata_dict['politicalGeocodingLevelURI'] = "http://dcat-ap.de/def/politicalGeocoding/Level/state"
        metadata_dict['politicalGeocodingURI'] = "[\"http://dcat-ap.de/def/politicalGeocoding/stateKey/02\"]"

        expected_payload = self._build_expected_payload(pkg_dict, metadata_dict, plugin)

        mock_post.assert_called_once_with(
            plugin.get_search_index_endpoint(),
            auth=('testuser', 'testpassword'),
            headers={'Content-Type': 'application/json'},
            data=ANY
        )
        self._check_payload(expected_payload, mock_post)

    @patch('ckanext.searchindexhook.plugin.requests.post')
    def test_add_to_index_extra_values_modified_date_in_future(self, mock_post):
        plugin = self._build_plugin_add_index()

        date_in_future = datetime.datetime.max.strftime("%Y-%m-%dT%H:%M:%S%z")
        data_dict = {
            "resources": [{
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4"
            }],
            "extras": [{
                "key": "modified",
                "value": date_in_future
            }]
        }

        pkg_dict = self._build_pkg_dict(data_dict)

        plugin.add_to_index(pkg_dict)

        metadata_dict = self._build_metadata_dict(pkg_dict, data_dict)
        metadata_dict['dct_modified'] = datetime.datetime.max.strftime(NORMALIZED_DATE_FORMAT)

        expected_payload = self._build_expected_payload(pkg_dict, metadata_dict, plugin)

        mock_post.assert_called_once_with(
            plugin.get_search_index_endpoint(),
            auth=('testuser', 'testpassword'),
            headers={'Content-Type': 'application/json'},
            data=ANY
        )
        self._check_payload(expected_payload, mock_post)

    @patch('ckanext.searchindexhook.plugin.requests.post')
    def test_add_to_index_extra_values_invalid_date(self, mock_post):
        plugin = self._build_plugin_add_index()

        data_dict = {
            "resources": [{
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4"
            }],
            "extras": [{
                "key": "temporal_start",
                "value": "2016/17"
            }]
        }

        pkg_dict = self._build_pkg_dict(data_dict)

        # execute
        plugin.add_to_index(pkg_dict)

        # assert
        metadata_dict = self._build_metadata_dict(pkg_dict, data_dict)

        expected_payload = self._build_expected_payload(pkg_dict, metadata_dict, plugin)

        mock_post.assert_called_once_with(
            plugin.get_search_index_endpoint(),
            auth=('testuser', 'testpassword'),
            headers={'Content-Type': 'application/json'},
            data=ANY
        )
        self._check_payload(expected_payload, mock_post)

    def test_normalize_date_valid_values(self):
        plugin = self._build_plugin_add_index()

        expected = '2017-08-24 11:19:57'

        valid_values = ['2017-08-24T11:19:57+02:00', '2017-08-24T11:19:57+0200', '2017-08-24T11:19:57.133814']
        for value in valid_values:
            actual = plugin.normalize_date(value)
            self.assertEqual(actual, expected)

        # without time
        actual = plugin.normalize_date('20170824')
        self.assertEqual(actual, '2017-08-24 00:00:00')

    def test_normalize_date_invalid_values(self):
        plugin = self._build_plugin_add_index()

        invalid_values = ['24082017', 'foo', '']
        for value in invalid_values:
            with self.assertRaises(ValueError):
                actual = plugin.normalize_date(value)
                self.assertEqual(actual, None)

        # TypeError if required param is None
        with self.assertRaises(TypeError):
            actual = plugin.normalize_date()
            self.assertEqual(actual, None)

    @patch('ckanext.searchindexhook.plugin.requests.delete')
    def test_delete_from_index_works_as_expected(self, mock_delete):
        plugin = self.get_plugin_instance()

        document_id = 'test-name-17'
        mocked_id_value = 'testid-17'
        type_value = 'test_type'
        name_value = 'test-name-17'
        mocked_pkg_dict = {
            'id': mocked_id_value,
            'type': type_value,
            'name': name_value
        }
        plugin.search_index_endpoint = 'http://www.ws.de/test/'
        plugin.search_index_credentials = 'testuser:testpassword'
        plugin.targetlink_url_base_path = '/test/path/'
        plugin.search_index_name = 'test-index'

        plugin.resolve_data_dict = Mock(
            return_value=mocked_pkg_dict
        )

        plugin.delete_from_index(document_id)

        expected_payload = [{
            'indexName': plugin.search_index_name,
            'type': type_value,
            'version': None,
            'displayName': None,
            'document': {
                'id': mocked_id_value,
                'title': None,
                'sprache': None,
                'sections': [],
                'tags': [],
                'mandant': 1,
                'metadata': None
            }
        }]

        mock_delete.assert_called_once_with(
            plugin.get_search_index_endpoint() + mocked_id_value,
            auth=('testuser', 'testpassword'),
            headers={'Content-Type': 'application/json'},
            data=ANY
        )
        self._check_payload(expected_payload, mock_delete)

    def test_http_error_does_not_block_before_index(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'indexable_dataset'

        pre_mock_def = plugin.delete_from_index
        plugin.delete_from_index = Mock(
            side_effect=HTTPError('test-error-message')
        )

        pkg_dict = {'id': 15, 'name': 'package-1', 'type': 'indexable_dataset'}

        non_blocked_return = plugin.before_index(pkg_dict)

        self.assertEquals(
            pkg_dict,
            non_blocked_return
        )

        plugin.delete_from_index = pre_mock_def

    def test_http_error_does_not_block_after_delete(self):
        plugin = self.get_plugin_instance()

        pre_mock_def = plugin.delete_from_index
        plugin.delete_from_index = Mock(
            side_effect=HTTPError('test-error-message')
        )

        pkg_dict = {'id': 15, 'name': 'package-1'}

        non_blocked_return = plugin.after_delete([], pkg_dict)

        self.assertEquals(
            None,
            non_blocked_return
        )

        plugin.delete_from_index = pre_mock_def

    def test_connection_error_does_not_block_before_index(self):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'indexable_dataset'

        pre_mock_def = plugin.delete_from_index
        plugin.delete_from_index = Mock(
            side_effect=ConnectionError('test-error-message')
        )

        pkg_dict = {'id': 15, 'name': 'package-1', 'type': 'indexable_dataset'}

        non_blocked_return = plugin.before_index(pkg_dict)

        self.assertEquals(
            pkg_dict,
            non_blocked_return
        )

        plugin.delete_from_index = pre_mock_def

    def test_shorten_resource_formats_empty(self):
        plugin = self.get_plugin_instance()

        resources_dict = [
            {}, {"format": ""}, {"format": "CSV"},
            {"format": "http://publications.europa.eu/resource/authority/file-type/CSV"},
            {"format": "https://publications.europa.eu/resource/authority/file-type/CSV"},
            {"format": "http://publications.europa.eu/mdr/resource/authority/file-type/CSV"},
            {"format": "https://publications.europa.eu/resource/authority/file-type/CSV"},
            {"format": "http://www.iana.org/assignments/media-types/text/csv"},
            {"format": "https://www.iana.org/assignments/media-types/text/csv"}
        ]
        expected_values = [
            None, "", "CSV", "CSV", "CSV", "CSV", "CSV", "text/csv", "text/csv"
        ]

        # execute
        plugin.shorten_resource_formats(resources_dict)

        # assert
        for num, resource_dict in enumerate(resources_dict):
            self.assertEquals(expected_values[num], resource_dict.get('format', None))

    def test_connection_error_does_not_block_after_delete(self):
        plugin = self.get_plugin_instance()

        pre_mock_def = plugin.delete_from_index
        plugin.delete_from_index = Mock(
            side_effect=ConnectionError('test-error-message')
        )

        pkg_dict = {'id': 15, 'name': 'package-1'}

        non_blocked_return = plugin.after_delete([], pkg_dict)

        self.assertEquals(
            None,
            non_blocked_return
        )

        plugin.delete_from_index = pre_mock_def

    def test_calculate_geojson_area(self):
        # Polygon with two holes
        spatial = geojson.Polygon([
            [
                [8.031005859375, 51.24128576954669],
                [10.3656005859375, 51.436888577204996],
                [10.4974365234375, 50.1135334310997],
                [8.4320068359375, 50.0289165635219],
                [8.031005859375, 51.24128576954669]
            ],
            [
                [8.7451171875, 51.020666012558095],
                [9.9700927734375, 51.02412130394265],
                [9.9481201171875, 50.2682767372753],
                [8.800048828125, 50.306884231551166],
                [8.7451171875, 51.020666012558095]
            ],
            [
                [9.667968749999998, 51.26878915771344],
                [10.0634765625, 51.327179239685634],
                [10.1348876953125, 51.037939894299356],
                [9.755859375, 51.089722918116344],
                [9.667968749999998, 51.26878915771344]
            ]
        ])

        plugin = self.get_plugin_instance()
        area = plugin.calculate_geojson_area(spatial)

        actual_area = 14626176108.445526
        self.assertTrue(area > actual_area - 100 and area < actual_area + 100)

    def test_spatial_to_meta_geojson_type_point(self):
        # prepare
        extra = {}
        extra['key'] = 'spatial'
        extra['value'] = '{"type": "Point", "coordinates": [9.156908, 53.896117]}'
        metadata_dict = {}
        metadata_dict['name'] = 'test-dict-name'

        # execute
        plugin = self.get_plugin_instance()
        plugin.spatial_to_meta(extra, metadata_dict)

        # validate
        self.assertEqual(metadata_dict['boundingbox'], json.loads(extra['value']))
        self.assertEqual(metadata_dict['spatial_area'], 0)
        self.assertEqual(metadata_dict['spatial_center'], {'lat': 53.896117, 'lon': 9.156908})

    def test_spatial_to_meta_geojson_type_polygon_fix(self):
        # prepare
        extra = {}
        extra['key'] = 'spatial'
        extra['value'] = '''{"type": "polygon", "coordinates":[
          [
            [
              9.11590576171875,
              47.62097541515849
            ],
            [
              9.2340087890625,
              47.62097541515849
            ],
            [
              9.2340087890625,
              47.70421683390384
            ],
            [
              9.11590576171875,
              47.70421683390384
            ],
            [
              9.11590576171875,
              47.62097541515849
            ]
          ]
        ]}'''
        metadata_dict = {}
        metadata_dict['name'] = 'test-dict-name'

        # execute
        plugin = self.get_plugin_instance()
        plugin.spatial_to_meta(extra, metadata_dict)

        # validate
        fixed_spatial_source = extra['value'].replace(
                'polygon',
                'Polygon'
            )
        self.assertEqual(metadata_dict['boundingbox'], json.loads(fixed_spatial_source))
        self.assertEqual(metadata_dict['spatial_area'], 82049776.65255576)
        self.assertEqual(metadata_dict['spatial_center'],
                         {'lat': 47.66259612453116, 'lon': 9.174957275390625})

    def test_remove_duplicate_coordinates(self):
        # prepare
        extra = {}
        extra['key'] = 'spatial'
        extra['value'] = '''{"type": "Polygon", "coordinates":[
          [
            [
              9.11590576171875,
              47.62097541515849
            ],
            [
              9.2340087890625,
              47.62097541515849
            ],
            [
              9.2340087890625,
              47.62097541515849
            ],
            [
              9.2340087890625,
              47.70421683390384
            ],
            [
              9.11590576171875,
              47.70421683390384
            ],
            [
              9.11590576171875,
              47.62097541515849
            ]
          ]
        ]}'''
        metadata_dict = {}
        metadata_dict['name'] = 'test-dict-name'

        # execute
        plugin = self.get_plugin_instance()
        plugin.spatial_to_meta(extra, metadata_dict)

        # validate
        expected_coordinates = [
            [
              9.11590576171875,
              47.62097541515849
            ],
            [
              9.2340087890625,
              47.62097541515849
            ],
            [
              9.2340087890625,
              47.70421683390384
            ],
            [
              9.11590576171875,
              47.70421683390384
            ],
            [
              9.11590576171875,
              47.62097541515849
            ]
        ]
        self.assertListEqual(metadata_dict['boundingbox']['coordinates'][0], expected_coordinates)

    def test_aggregate_quality_metrics_both_in_dict_as_expected(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "format": "csv",
                "access_url": "http://domain.com"
            }
        ]

        self.assertEquals(
            (True, True),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def test_aggregate_quality_metrics_both_not_in_dict(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4"
            }
        ]

        self.assertEquals(
            (False, False),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def test_aggregate_quality_metrics_access_url_not_in_dict(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "format": "csv"
            }
        ]

        self.assertEquals(
            (False, True),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def test_aggregate_quality_metrics_mimetype_in_dict_format_not(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "mimetype": "text/csv"
            }
        ]

        self.assertEquals(
            (False, True),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def test_aggregate_quality_metrics_format_not_in_dict(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "access_url": "http://domain.com"
            }
        ]

        self.assertEquals(
            (True, False),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def test_aggregate_quality_metrics_access_url_fallback_without_download_url(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "url": "http://domain.com"
            }
        ]

        self.assertEquals(
            (True, False),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def test_aggregate_quality_metrics_access_url_fallback_download_url_different(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "url": "http://domain.com",
                "download_url": "http://domain2.com"
            }
        ]

        self.assertEquals(
            (True, False),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def test_aggregate_quality_metrics_access_url_fallback_download_url_same(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "url": "http://domain.com",
                "download_url": "http://domain.com"
            }
        ]

        self.assertEquals(
            (False, False),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def test_aggregate_quality_metrics_multiple_resources_only_in_one_resource(self):
        plugin = self.get_plugin_instance()

        resources_dict_list = [
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "access_url": "http://domain.com"
            },
            {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
                "format": "csv"
            }
        ]

        self.assertEquals(
            (True, True),
            plugin.aggregate_quality_metrics(resources_dict_list)
        )

    def get_plugin_instance(self, plugin_name='search_index_hook'):
        '''
        Return a plugin instance by name.
        '''
        if not ckan.plugins.plugin_loaded(plugin_name):
            ckan.plugins.load(plugin_name)
        plugin = ckan.plugins.get_plugin(plugin_name)
        self.assertNotEquals(None, plugin)

        return plugin
