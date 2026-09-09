# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [6.8.0] - 2026-09-03

### Changed
- Compatibility with latest setuptools (added `setuptools_scm` for pip 25.3+ / setuptools 80+, temporary pin `setuptools<81`)
- Systemtests use Java 17 and Maven 3.9
- Removed `pytest-ckan` from `dev-requirements.txt` — the PyPI package (0.0.7, 2020) is deprecated and hard-depends on Pylons, which CKAN dropped in 2.9. The tests use `unittest.TestCase` + `pytest.raises` only, so no fixtures are lost
- CI installs CKAN 2.10.5 directly from the official GitHub release tarball (`https://github.com/ckan/ckan/archive/refs/tags/ckan-2.10.5.tar.gz`) with its `requirements.txt` pre-installed, instead of `pip install ckan` from PyPI — the PyPI `ckan` distribution is a stale pre-2.9 release. `libpq-dev`, `libxml2-dev`, `libxslt1-dev`, `libmagic1`, `libjpeg-dev` and `zlib1g-dev` are installed via `apt-get` first for `psycopg2`, `lxml`, `python-magic` (and defensively for Pillow-family transitives). `CKAN_SITE_URL` is set as a pipeline-level variable so CKAN's config validation passes when the first test triggers `ckan.plugins.load()`

### Fixed
- Support for GeoJSON type `GeometryCollection` in `spatial_to_meta` — previously crashed silently and left `boundingbox`, `spatial_area` and `spatial_center` unset
- Sync `dataset_purge` to the search index — hard-deleted packages no longer leave orphan documents in Elasticsearch

## [6.7.0] - 2024-03-26

### Added
- Support for `dcatap:applicableLegislation` and `dcatap:hvdCategory`

## [6.1.0] - 2023-08-01

### Changed
- Updates and cleans up dependencies
- Standardization of the `test.ini` file

## [6.0.0] - 2023-07-05

### Removed
- Support for CKAN versions prior 2.9 and Python 2

## [5.13.0] - 2023-05-04

### Added
- Support for CKAN 2.10.0

## [5.8.0] - 2022-12-15

### Added
- DataService flag to the search index

## [5.6.0] - 2022-11-03

### Added
- Support for `dcat:bbox` and `dcat:centroid`

### Changed
- Updated pylint configuration to latest version and fixed several warnings

## [5.5.0] - 2022-10-20

### Changed
- Do not save `format` in the Elasticsearch searchindex if the value is an empty string

## [5.4.0] - 2022-09-12

### Changed
- Internal release: switched Python environment from 3.6 to 3.8 and updated deployment scripts

## [5.1.0] - 2022-04-07

### Added
- Support for Python 3

## [5.0.0] - 2022-03-24

### Changed
- Update to Elasticsearch 7.x: changes index-queue-service request body

### Fixed
- `dev-requirements.txt`: banned broken version 1.7.0 of `lazy-object-proxy`

## [4.6.2] - 2021-11-23

### Changed
- Explicitly disallow incorrect version of `python-dateutil`

## [4.6.0] - 2021-11-04

### Added
- `contributorID` in extras as explicitly defined field

### Fixed
- Save explicitly defined fields of type list as list instead of as string

## [4.3.2] - 2021-01-28

### Added
- New attributes for metadata quality metrics

### Changed
- Introduce `.gitattributes` and fix line endings

## [3.7.0] - 2019-12-19

### Added
- Workaround for compatibility with Pylons/Flask to the latest CKAN versions
- Log message when license list is missing

### Changed
- Removed the restriction to a specific version of CKAN in dev requirements as well

## [3.6.2] - 2019-11-28

### Changed
- Removed the restriction to a specific version of CKAN

### Fixed
- Ignore date in field `dct:modified` for sorting field if the date is in the future

## [3.6.1] - 2019-11-08

### Changed
- Renamed environment names for internal CI/CD pipeline

### Fixed
- Problem with version 2.8.1 of `python-dateutil` (raises unexpected `IndexError` instead of `ParserError`)

## [3.4.0] - 2019-04-25

### Changed
- GeoJSON parsing: remove duplicate coordinates

### Fixed
- GeoJSON parsing: problem with GeoJSON type `Point`

## [3.2.0] - 2018-12-21

### Added
- Shortened resource formats into search index

### Changed
- Improved exception handling for spatial validation
- Improved date parsing

## [3.0.1] - 2017-12-20

### Added
- Support DCAT-AP.de

## [2.3.0] - 2016-06-01

### Added
- Initial commit "Regelbetrieb"
