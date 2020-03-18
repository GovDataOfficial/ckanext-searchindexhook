"""
Module for pushing data into the search index.
"""
import datetime
import json
import logging

from area import area
import ckan.model as model
import ckan.plugins as plugins
import geojson
import pylons.config as config
import requests
from requests.exceptions import HTTPError, ConnectionError
from shapely.geometry import shape
from dateutil.parser import parse

LOGGER = logging.getLogger(__name__)

NORMALIZED_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class SearchIndexHookPlugin(plugins.SingletonPlugin):
    """
    Plugin for adding and deleting package data from the bmi-govdata
    search index.
    """
    plugins.implements(plugins.IPackageController, inherit=True)

    search_index_endpoint = config.get(
        'ckan.searchindexhook.endpoint',
        False
    )

    search_index_credentials = config.get(
        'ckan.searchindexhook.endpoint.credentials',
        False
    )

    indexable_data_types = config.get(
        'ckan.searchindexhook.indexable.data.types',
        False
    )

    targetlink_url_base_path = config.get(
        'ckan.searchindexhook.targetlink.url.base.path',
        False
    )

    search_index_name = config.get(
        'ckan.searchindexhook.index.name',
        False
    )

    # IPackageController

    def __init__(self, **kwargs):
        # Workaround until the core translation function defaults to the Flask one
        from paste.registry import Registry
        from ckan.lib.cli import MockTranslator
        registry = Registry()
        registry.prepare()
        from pylons import translator
        registry.register(translator, MockTranslator())

        # Load license information once
        self.license_openness_map = self.load_license_openness()

    @staticmethod
    def load_license_openness():
        """
        Loads the list of licenses from CKAN and stores a mapping from license-ids to the "is-open" flag.
        """
        try:
            context = {'model': model, 'ignore_auth': True}
            license_list = plugins.toolkit.get_action('license_list')(context, {})

            license_openness_map = {}
            for license in license_list:
                license_openness_map[license["id"]] = license["is_okd_compliant"] or \
                                                      license["is_osi_compliant"]

            return license_openness_map
        except Exception as err:
            LOGGER.warn('Could not load license list for openness calculation! Details: %s', err)
            return {}

    @staticmethod
    def shorten_resource_formats(resources_dict):
        """
        Replaces URI values in resource formats, such that a search for e.g. 'CSV' matches
        both literal values and the media type or MDR resource URIs.
        """
        prefixes = [
            'http://www.iana.org/assignments/media-types/',
            'https://www.iana.org/assignments/media-types/',
            'http://publications.europa.eu/resource/authority/file-type/',
            'https://publications.europa.eu/resource/authority/file-type/',
            'http://publications.europa.eu/mdr/resource/authority/file-type/',
            'https://publications.europa.eu/mdr/resource/authority/file-type/'
        ]

        for res in resources_dict:
            res_format = res.get('format')
            if res_format:
                for prefix in prefixes:
                    if res_format.startswith(prefix):
                        res_format = res_format.replace(prefix, '')
                res['format'] = res_format

    @classmethod
    def assert_endpoint_configuration(cls, value):
        """
        Asserts that search index endpoint is configured.
        """
        assert_message = 'Configured endpoint is not a value'
        assert isinstance(value, basestring), assert_message

    @classmethod
    def assert_credentials_configuration(cls, value):
        """
        Asserts that search index credentials are configured.
        """
        assert_message = 'Configured credentials are not a string'
        assert isinstance(value, basestring), assert_message
        assert_message = ('Credentials not configured',
                          'in format username:password')
        assert len(value.split(':')) == 2, assert_message

    @classmethod
    def assert_targetlink_url_base_path(cls, value):
        """
        Asserts that the targetlink URL base path is configured.
        """
        assert_message = 'Configured URL base path is not a string'
        assert isinstance(value, basestring), assert_message

    @classmethod
    def assert_search_index_name(cls, value):
        """
        Asserts that the search index name is configured.
        """
        assert_message = 'Configured index name is not a string'
        assert isinstance(value, basestring), assert_message

    @classmethod
    def assert_mandatory_dict_keys(cls, data_dict):
        """
        Asserts that the dict contains the mandatory keys.
        """
        assert_message = "Dictionary does not contain key 'data_dict'"
        assert 'data_dict' in data_dict, assert_message

        data_dict_from_json = json.loads(data_dict['data_dict'])

        assert_message = "Dictionary does not contain key 'resources'"
        assert 'resources' in data_dict_from_json, assert_message

        assert_message = "Dictionary does not contain key 'extras'"
        assert 'extras' in data_dict_from_json, assert_message

    def assert_configuration(self):
        """
        Asserts / guards the configuration of this plugin.
        """
        self.assert_endpoint_configuration(
            self.search_index_endpoint
        )
        self.assert_credentials_configuration(
            self.search_index_credentials
        )
        self.assert_targetlink_url_base_path(
            self.targetlink_url_base_path
        )
        self.assert_search_index_name(
            self.search_index_name
        )

    def get_search_index_credentials(self):
        """
        Returns the configured HTTP basic auth credentials for
        the search index webservice as a dictionary.
        """
        credentials = self.search_index_credentials.split(':')
        return {
            'username': credentials[0],
            'password': credentials[1]
        }

    def get_indexable_data_types(self):
        """
        Returns the configured indexable data types to add to
        the search index as a list.
        """
        return [x.strip() for x in self.indexable_data_types.split(',')]

    def should_be_indexed(self, dataset_type):
        """
        Returns if a given dataset type should be index based on the
        configured accepted data types.
        """
        indexable_data_types = self.get_indexable_data_types()

        return dataset_type.strip() in indexable_data_types

    def get_targetlink_url_base_path(self):
        """
        Returns the configured targetlink URL base path. If configured value
        misses an slash (/) it's added.
        """
        if self.targetlink_url_base_path[-1] == '/':
            return self.targetlink_url_base_path
        return self.targetlink_url_base_path + '/'

    def get_search_index_endpoint(self):
        """
        Returns the configured search index endpoint. If configured value
        misses an slash (/) it's added.
        """
        if self.search_index_endpoint[-1] == '/':
            return self.search_index_endpoint
        return self.search_index_endpoint + '/'

    def substitute_targetlink(self, dataset_name):
        """
        Returns a substituted targetlink (i.e. combination of configured
        targetlink URL base path and the name of the dataset).
        """
        return '{base_path}{dataset_name}'.format(
            base_path=self.get_targetlink_url_base_path(),
            dataset_name=dataset_name
        )

    def before_index(self, pkg_dict):
        """
        CKAN hook point for dataset addition. Before every addition
        a deletion is performed. Only "active" datasets will be index,
        "deleted" datasets are only deleted, but not updated.
        """
        LOGGER.debug("Syncing before Solr indexing")

        if 'type' not in pkg_dict:
            LOGGER.error('No package / dataset type set')

            return pkg_dict

        if not self.should_be_indexed(pkg_dict['type']):
            info_message = 'Skipping non indexable type: {type}'.format(
                type=pkg_dict['type']
            )

            LOGGER.info(info_message)

            return pkg_dict

        try:
            self.delete_from_index(pkg_dict['id'])
            self.add_to_index(pkg_dict)
        except HTTPError as error:
            error_message = 'Request failed with: {message}'.format(
                message=error.message
            )
            LOGGER.error(error_message)
        except ConnectionError as error:
            error_message = 'Endpoint is not available: {message}'.format(
                message=error.message
            )
            LOGGER.error(error_message)

        return pkg_dict

    def calculate_geojson_area(self, spatial):
        """
        Calculates the area of the spatial feature
        """
        return area(spatial)

    def calculate_geojson_center(self, spatial):
        """
        Calculates the center point of the given Polygon and returns the coordinates
        """
        shapelyPolygon = shape(spatial)
        centroid = shapelyPolygon.centroid
        return centroid.x, centroid.y

    def add_to_index(self, data_dict):
        """
        Adds a dataset to the search index.
        """
        self.assert_configuration()
        self.assert_mandatory_dict_keys(data_dict)

        # 'data_dict' comes as a string
        data_dict_from_json = json.loads(data_dict['data_dict'])
        resources_dict = data_dict_from_json['resources']
        self.shorten_resource_formats(resources_dict)
        extras_dict = data_dict_from_json['extras']

        credentials = self.get_search_index_credentials()
        has_open, has_closed = self.aggregate_openness(resources_dict)

        metadata_dict = {
            'state': data_dict['state'],
            'private': data_dict['private'],
            'name': data_dict['name'],
            'has_open': has_open,
            'has_closed': has_closed,
            'resources_licenses': self.aggregate_licenses(resources_dict),
            'author': data_dict['author'],
            'author_email': data_dict['author_email'],
            'maintainer': data_dict['maintainer'],
            'maintainer_email': data_dict['maintainer_email'],
            'groups': data_dict['groups'],
            'notes': data_dict['notes'],
            'metadata_created': data_dict['metadata_created'],
            'metadata_modified': data_dict['metadata_modified'],
            'dct_modified_fallback_ckan': data_dict['metadata_modified'],
            'type': data_dict['type'],
            'owner_org': data_dict['owner_org'],
            'resources': resources_dict,
            'extras': extras_dict
        }

        # prepare data from extras to be used in search
        for extra in extras_dict:
            try:
                # if there are geo data, extract them
                if extra['key'] == 'spatial' and extra['value'] != '':
                    self.spatial_to_meta(extra, metadata_dict)
                # prepare time coverage for easier search
                elif extra['key'] == 'temporal_start' and extra['value'] != '':
                    metadata_dict['temporal_start'] = self.normalize_date(
                        extra['value']
                    )
                elif extra['key'] == 'temporal_end' and extra['value'] != '':
                    metadata_dict['temporal_end'] = self.normalize_date(
                        extra['value']
                    )
                # dct:issued and dct:modified attributes
                elif extra['key'] == 'issued' and extra['value'] != '':
                    metadata_dict['dct_issued'] = self.normalize_date(
                        extra['value']
                    )
                elif extra['key'] == 'modified' and extra['value'] != '':
                    metadata_dict['dct_modified'] = self.normalize_date(
                        extra['value']
                    )
                    # set metadata_modified field to the extras value if available and the date is not
                    # in the future
                    dct_modified_date_obj_utc = datetime.datetime.strptime(
                        metadata_dict['dct_modified'], NORMALIZED_DATE_FORMAT
                        ).utctimetuple()
                    if dct_modified_date_obj_utc < datetime.datetime.now().utctimetuple():
                        metadata_dict['dct_modified_fallback_ckan'] = metadata_dict['dct_modified']
            except (ValueError, LookupError):
                info_message = "invalid date format in extras->" + extra['key']
                info_message += " at dataset: " + data_dict['name']
                info_message += ", value: " + extra['value']
                LOGGER.info(info_message)

        payload = [{
            'indexName': self.search_index_name,
            'type': data_dict['type'],
            'version': None,
            'displayName': None,
            'document': {
                'id': data_dict['id'],
                'title': data_dict['title'],
                'preamble': data_dict['notes'],
                'sprache': None,
                'sections': [],
                'tags': data_dict['tags'],
                'mandant': 1,
                'metadata': json.dumps(metadata_dict),
                'targetlink': self.substitute_targetlink(data_dict['name'])
            }
        }]

        info_message = 'Endpoint to call against: {endpoint}'.format(
            endpoint=self.get_search_index_endpoint()
        )
        LOGGER.debug(info_message)

        request = requests.post(
            self.get_search_index_endpoint(),
            auth=(credentials['username'], credentials['password']),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )

        info_message = "Adding to index: id={id}, name={name}".format(
            id=data_dict['id'],
            name=data_dict['name']
        )
        LOGGER.debug(info_message)

        info_message = "Service response status code: (code={code})".format(
            code=request.status_code
        )
        LOGGER.debug(info_message)
        request.raise_for_status()

    @staticmethod
    def aggregate_licenses(resources_dict):
        """Returns an array containing all license IDs from the given resources."""
        licenses = set()  # Set, so we don't get double entries
        for resource in resources_dict:
            if "license" in resource:
                licenses.add(resource["license"])

        return list(licenses)

    def aggregate_openness(self, resources_dict):
        """
        Returns a tuple containing two booleans with information about the openness of licenses of
        the given resources: (has_open, has_closed)
        """
        has_open = False
        has_closed = False

        for resource in resources_dict:
            if "license" in resource and resource["license"] in self.license_openness_map:
                openness = self.license_openness_map[resource["license"]]
                has_open = has_open or openness
                has_closed = has_closed or not openness

        return has_open, has_closed

    def spatial_to_meta(self, extra, metadata_dict):
        """
        Helper to get GeoJSON from extras->spatial into a metadata_dict for the given
        extra item
        """
        # check for valid GeoJSON to prevent ckan
        # from rejecting the whole dataset
        try:
            # fix invalid Polygon-Features
            # (because - yes - people have problems reading the spec)
            fixed_spatial_source = extra['value'].replace(
                'polygon',
                'Polygon'
            )

            spatial = geojson.loads(fixed_spatial_source)
            spatial_validation = geojson.is_valid(spatial)

            if spatial_validation['valid'] == 'yes':
                # - additional check: does the interior share more
                #   than 1 point with exterior? --> invalid
                # - exclude GeoJSON type Point
                if len(spatial.coordinates) > 1 and isinstance(spatial.coordinates[0], list):
                    # check all internal polygons
                    for internal_polygon in spatial.coordinates[1:]:
                        shared_coordinates_counter = 0
                        # iterate external coordinates,
                        # see if >1 matches internal polygon
                        for coord_external in spatial.coordinates[0]:
                            if coord_external in internal_polygon:
                                shared_coordinates_counter += 1
                            if shared_coordinates_counter > 1:
                                # skip spatial coordinates
                                raise ValueError('More than one shared coordinate!')

                # extract string to JSON and remove potential duplicate coordinates using shapely
                # cf. https://stackoverflow.com/questions/49330030/remove-a-duplicate-point-from-polygon-in-shapely?rq=1
                # dump and load to get unicode strings in dicts.
                metadata_dict['boundingbox'] = json.loads(
                    geojson.dumps(shape(spatial).simplify(0))
                )

                # calculate area covered by the the shape
                spatial_area = self.calculate_geojson_area(spatial)

                # area must at least be >0. We are using 1/X to rank the results
                if spatial_area < 0:
                    spatial_area = 1

                metadata_dict['spatial_area'] = spatial_area

                # calculate center of the shape
                spatial_center_x, spatial_center_y = self.calculate_geojson_center(
                    spatial
                )
                metadata_dict['spatial_center'] = {
                    "lat": spatial_center_y,
                    "lon": spatial_center_x
                }
            else:
                raise ValueError(spatial_validation['message'])
        except Exception as ex:
            info_message = "invalid GeoJSON in extras->spatial "
            info_message += "at dataset: " + metadata_dict['name']
            info_message += ", value: " + fixed_spatial_source
            info_message += ", Exception: "
            info_message += type(ex).__name__
            info_message += ", "
            info_message += str(ex.args)
            LOGGER.info(info_message)

    def normalize_date(self, datestr):
        """
        Normalizes date strings
        """
        # formats equal to govdata-DateUtil Java class
        dateformats = [
            "yyyy-MM-dd'T'HH:mm:ssX",
            "yyyy-MM-dd'T'HH:mm:ssz",
            "yyyy-MM-dd'T'HH:mm:ss",
            "yyyy-MM-dd HH:mm:ssX",
            "yyyy-MM-dd HH:mm:ssz",
            "yyyy-MM-dd HH:mm:ss X",
            "yyyy-MM-dd HH:mm:ss z",
            "yyyy-MM-dd HH:mm:ss",
            "yyyy-MM-dd",
            "dd.MM.yyyy'T'HH:mm:ssX",
            "dd.MM.yyyy'T'HH:mm:ssz",
            "dd.MM.yyyy'T'HH:mm:ss",
            "dd.MM.yyyy HH:mm:ss",
            "dd.MM.yyyy"
        ]

        for dateformat in dateformats:
            try:
                parseddate = datetime.datetime.strptime(
                    datestr,
                    self.transform_date_notation(dateformat)
                )

                return parseddate.strftime(NORMALIZED_DATE_FORMAT)
            except ValueError:
                pass

        # Use dateutil as fallback, e.g. for time offset with colon: +02:00
        parseddate = parse(datestr)
        return parseddate.strftime(NORMALIZED_DATE_FORMAT)

    @classmethod
    def transform_date_notation(cls, notation):
        """
        Transforms date notations
        """
        translations = [
            ["yyyy", "%Y"],
            ["MM", "%m"],
            ["dd", "%d"],
            ["HH", "%H"],
            ["mm", "%M"],
            ["ss", "%S"],
            ["'T'", "T"],
            ["z", "%Z"],
            ["X", "%z"]
        ]

        for translation in translations:
            notation = notation.replace(
                translation[0],
                translation[1]
            )

        return notation

    @classmethod
    def resolve_data_dict(cls, document_id, context=None):
        """
        Resolves the data dict by id
        """
        package_show = plugins.toolkit.get_action('package_show')

        if not context:
            context = {'model': model, 'ignore_auth': True}

        try:
            package_dict = package_show(
                context,
                {'id': document_id.strip()}
            )

            return package_dict
        except Exception as not_found:
            log_message = "Dataset for id {id} was not found".format(
                id=document_id
            )
            LOGGER.error(log_message)

            raise Exception(not_found)

    def delete_from_index(self, document_id, context=None):
        """
        Deletes a dataset from the search index.
        """
        self.assert_endpoint_configuration(
            self.search_index_endpoint
        )

        credentials = self.get_search_index_credentials()

        # resolve package dict, because CKAN gives us sometimes the name instead of the id
        package_dict = self.resolve_data_dict(document_id, context)
        real_package_id = package_dict['id']

        payload = [{
            'indexName': self.search_index_name,
            'type': package_dict['type'],
            'version': None,
            'displayName': None,
            'document': {
                'id': real_package_id,
                'title': None,
                'sprache': None,
                'sections': [],
                'tags': [],
                'mandant': 1,
                'metadata': None
            }
        }]

        info_message = 'Endpoint to call against: {endpoint}'.format(
            endpoint=self.get_search_index_endpoint() + real_package_id
        )
        LOGGER.debug(info_message)

        request = requests.delete(
            self.get_search_index_endpoint() + real_package_id,
            auth=(credentials['username'], credentials['password']),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )

        info_message = "Deleting from index: (id={id}, name={name})".format(
            id=real_package_id, name=package_dict['name']
        )
        LOGGER.debug(info_message)
        info_message = "Service reponse status code: (code={code})".format(
            code=request.status_code
        )
        LOGGER.debug(info_message)
        request.raise_for_status()

    def after_delete(self, context, data_dict):
        """
        CKAN hook point for dataset deletion.
        """
        LOGGER.debug("Syncing after package deletion")

        try:
            self.delete_from_index(
                data_dict['id'],
                context
            )
        except HTTPError as error:
            error_message = 'Request failed with: {message}'.format(
                message=error.message
            )
            LOGGER.error(error_message)
        except ConnectionError as error:
            error_message = 'Endpoint is not available: {message}'.format(
                message=error.message
            )
            LOGGER.error(error_message)
