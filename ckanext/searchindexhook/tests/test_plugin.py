# -*- coding: utf-8 -*-
'''
Tests for the ckanext.searchindexhook extension.
'''
import pylons.config as config
import webtest
import unittest
import ckan.model as model
import ckan.plugins
import json
import geojson

from nose.tools import assert_raises
from mock import Mock, patch
from requests.exceptions import HTTPError, ConnectionError


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
            "resources": {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
            },
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
            "resources": {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
            },
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

    @patch('ckanext.searchindexhook.plugin.requests.post')
    def test_add_to_index_works_as_expected(self, mock_post):
        plugin = self.get_plugin_instance()
        plugin.indexable_data_types = 'indexable_dataset'
        plugin.search_index_endpoint = 'http://www.ws.de/test/'
        plugin.search_index_credentials = 'testuser:testpassword'
        plugin.targetlink_url_base_path = '/test/path/'
        plugin.search_index_name = 'test-index'

        data_dict = {
            "resources": {
                "cache_last_updated": None,
                "package_id": "f73d8b97-e6cb-46bf-bbf6-670155f9fbb4",
            },
            "extras": [{
                "key": "value"
            }]
        }

        pkg_dict = {
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

        plugin.add_to_index(pkg_dict)

        metadata_dict = {
            'state': pkg_dict['state'],
            'private': pkg_dict['private'],
            'name': pkg_dict['name'],
            'isopen': pkg_dict['isopen'],
            'author': pkg_dict['author'],
            'author_email': pkg_dict['author_email'],
            'maintainer': pkg_dict['maintainer'],
            'maintainer_email': pkg_dict['maintainer_email'],
            'groups': pkg_dict['groups'],
            'notes': pkg_dict['notes'],
            'license_id': pkg_dict['license_id'],
            'metadata_created': pkg_dict['metadata_created'],
            'metadata_modified': pkg_dict['metadata_modified'],
            'type': pkg_dict['type'],
            'owner_org': pkg_dict['owner_org'],
            'resources': data_dict['resources'],
            'extras': data_dict['extras']
        }

        expected_payload = [{
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

        mock_post.assert_called_once_with(
            plugin.get_search_index_endpoint(),
            auth=('testuser', 'testpassword'),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(expected_payload)
        )

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
            return_value = mocked_pkg_dict
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
            data=json.dumps(expected_payload)
        )

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
            [8.7451171875,51.020666012558095]
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
        self.assertTrue(area > actual_area -100 and area < actual_area + 100)

    def get_plugin_instance(self, plugin_name='search_index_hook'):
        '''
        Return a plugin instance by name.
        '''
        if not ckan.plugins.plugin_loaded(plugin_name):
            ckan.plugins.load(plugin_name)
        plugin = ckan.plugins.get_plugin(plugin_name)
        self.assertNotEquals(None, plugin)

        return plugin
