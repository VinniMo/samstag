import unittest
from unittest.mock import Mock

from bs4 import BeautifulSoup

from expanded_adapters import collect_expanded, parse_breche, parse_oblo
from samstag.collection.adapters.breche import parse_breche as packaged_parse_breche
from samstag.collection.adapters.oblo import parse_oblo as packaged_parse_oblo


class BrecheObloAdaptersTest(unittest.TestCase):
    def test_legacy_imports_use_packaged_adapters(self):
        self.assertIs(parse_breche, packaged_parse_breche)
        self.assertIs(parse_oblo, packaged_parse_oblo)

    def test_breche_dispatch_preserves_evidence_and_separates_doors_from_start(self):
        url = "https://www.la-breche.fun/"
        detail_url = url + "events/concert"
        programme = BeautifulSoup('<a href="/events/concert">Concert</a>', "lxml")
        detail = """
            <title>Concert · 13.11.2026</title>
            <div class="artist-div-2"><h2 class="h2-2">Concert</h2></div>
            <p>Portes : 19h Début : 20h30</p>
            <a href="https://petzi.ch/">Billetterie</a>
            <div class="rich-text-block">Programme officiel</div>
        """
        fetch = Mock(return_value=detail)
        result = collect_expanded(url, programme, fetch)
        fetch.assert_called_once_with(detail_url)
        event, = result.events
        self.assertEqual(event["source_event_key"], detail_url)
        self.assertEqual(event["evidence_url"], detail_url)
        self.assertEqual(event["location"], "La Brèche")
        self.assertEqual(event["event_kind"], "MusicEvent")
        self.assertEqual(event["description"], "Programme officiel")
        self.assertEqual(event["doors_time"], "19:00")
        self.assertEqual(event["start_at"], "2026-11-13T20:30:00+01:00")

    def test_oblo_dispatch_checks_visible_time_against_occurrence_url(self):
        url = "https://oblo.ch/"
        programme = BeautifulSoup("""
            <a href="/events/2026-11-13-20-30">
                <span>Vendredi</span><span>13 novembre</span><span>20h30</span>
                <span>Projection</span><span>Documentaire</span>
            </a>
            <a href="/events/2026-11-14-20-30">
                <span>Samedi</span><span>14 novembre</span><span>21h</span>
                <span>Performance</span><span>Performances</span>
            </a>
        """, "lxml")
        fetch = Mock()
        (first, second), adapter = collect_expanded(url, programme, fetch)
        fetch.assert_not_called()
        self.assertEqual(adapter, "oblo-programme-v3")
        self.assertEqual(first["evidence_url"], url)
        self.assertEqual(first["source_event_key"], url + "events/2026-11-13-20-30")
        self.assertEqual(first["event_kind"], "ScreeningEvent")
        self.assertEqual(first["start_at"], "2026-11-13T20:30:00+01:00")
        self.assertEqual(second["event_kind"], "TheaterEvent")
        self.assertFalse(second.get("start_at"))

    def test_oblo_rejects_missing_programme(self):
        with self.assertRaisesRegex(ValueError, "Programme Oblò absent"):
            parse_oblo(BeautifulSoup("<p>Programme</p>", "lxml"), "https://oblo.ch/")
