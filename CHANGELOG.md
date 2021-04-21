# Changelog

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
