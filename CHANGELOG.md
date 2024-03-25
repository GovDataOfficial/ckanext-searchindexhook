# Changelog

## v6.7.0 2024-03-26

* Adds support for dcatap:applicableLegislation and dcatap:hvdCategory

## v6.1.0 2023-08-01

* Updates and cleans up dependencies
* Standardization of the `test.ini` file

## v6.0.0 2023-07-05

* Removes support for old CKAN versions prior 2.9 and Python 2

## v5.13.0 2023-05-04

* Adds support for CKAN 2.10.0

## v5.8.0 2022-12-15

* Adds a DataService flag to the search index

## v5.6.0 2022-11-03

* Adds support for dcat:bbox and dcat:centroid
* Updates pylint configuration to latest version and fixes several warnings

## v5.5.0 2022-10-20

* Do not save 'format' in the Elasticsearch searchindex if value it's an empty string

## v5.4.0 2022-09-12

* Internal release: Switches Python environment from Python 3.6 to Python 3.8 and updating deployment scripts

## v5.1.0 2022-04-07

* Support for Python 3

## v5.0.0 2022-03-24

* Update to Elasticsearch 7.x: Changes index-queue-service request body
* Fixes dev-requirements.txt: Broken version 1.7.0 of lazy-object-proxy was banned

## v4.6.2 2021-11-23

* Explicitly disallow incorrect version of python-dateutil

## v4.6.0 2021-11-04

* Adds 'contributorID' in extras as explicitly defined field
* Saves as string defined explicitly defined fields of type list as list instead as string

## v4.3.2 2021-01-28

* Add new attributes for metadata quality metrics
* Introduce .gitattributes and fix line endings

## v3.7.0 2019-12-19

* Add workaround for compatibility with Pylons/Flask to the latest CKAN versions
* Remove the restriction to a specific version of CKAN in dev requirements as well
* Log when license list is missing

## v3.6.2 2019-11-28

* Remove the restriction to a specific version of CKAN
* Ignore date in field dct:modified for sorting field if the date is in the future

## v3.6.1 2019-11-08

* Rename environment names for internal ci/cd pipeline
* Fix problem with Version 2.8.1 of python-dateutil (raises unexpected IndexError instead of ParserError)

## v3.4.0 2019-04-25

* GeoJSON parsing: Add logic to remove duplicate coordinates
* GeoJSON parsing: Fix problem with GeoJSON type "Point"

## v3.2.0 2018-12-21

* Add shortened resource formats into search index
* Improve exception handling for spatial validation
* Improve date parsing

## v3.0.1 2017-12-20

* Support DCAT-AP.de

## v2.3.0 2016-06-01

* Initial commit "Regelbetrieb" (Version 2.3.0)
