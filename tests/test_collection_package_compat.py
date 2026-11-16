import unittest

import collection_result
import collection_worker
import scraper
import source_registry
from samstag.collection import registry, result, runner, worker
from samstag.collection.parsers import html, ical, jsonld


class CollectionPackageCompatibilityTest(unittest.TestCase):
    def test_legacy_modules_share_the_new_module_state(self):
        self.assertIs(scraper, runner)
        self.assertIs(source_registry, registry)
        self.assertIs(collection_result, result)
        self.assertIs(collection_worker, worker)

    def test_generic_parser_exports_are_the_packaged_functions(self):
        self.assertIs(scraper._extract_jsonld_events, jsonld._extract_jsonld_events)
        self.assertIs(scraper.parse_ics, ical.parse_ics)
        self.assertIs(scraper._extract_html_events, html._extract_html_events)
