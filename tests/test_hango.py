import json
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

from hango_adapter import collect_hango, parse_events
from source_registry import VENUES, source_for

SOURCE = source_for("https://etoileblanche.ch/")
VENUE = next(v for v in VENUES if v["id"] == "B007")


def node(id_, type_, music=True):
    return {"id":id_, "name":"Soirée synthétique", "startsAt":"2026-10-17T20:30:00Z",
            "endsAt":"2026-10-18T00:00:00Z", "rootEventId":"same-recurring-root",
            "description":"<p>Description synthétique</p>", "minPrice":None, "maxPrice":"0.00",
            "eventTagTerms":{"EVENT_TYPE":[{"tagTerm":{"name":type_}}], "MUSIC":[{}] if music else []}}


class HangoTest(unittest.TestCase):
    def test_structured_dj_theme_and_afterwork_are_distinguished(self):
        rows = parse_events({"nodes":[node("1","dj set"),node("2","afterwork"),node("3","soirée à thème"),node("4","soirée à thème",False)]}, SOURCE, VENUE, "https://example.test/widget")
        self.assertEqual(rows[0]["event_kind"], "MusicEvent")
        self.assertEqual(rows[0]["time"], "22:30")
        self.assertEqual(rows[0]["end_date"], "2026-10-18")
        self.assertEqual(rows[0]["price"], "Gratuit")
        self.assertNotIn("event_kind", rows[1])
        self.assertEqual(rows[2]["event_kind"], "ClubNight")
        self.assertNotIn("event_kind", rows[3])
        self.assertEqual(len({r["source_event_key"] for r in rows}), 4)

    def test_public_widget_identity_and_pagination_are_checked(self):
        html = '<iframe src="https://backoffice.hango.ch/external/widgets/estb_live_test"></iframe>'
        calls = []
        def fetch(url, extra_headers):
            calls.append(url)
            self.assertEqual(extra_headers, {"x-api-key":"estb_live_test"})
            if url.endswith('/establishment'):
                return json.dumps({"success":True,"data":{"name":"Etoile Blanche"}})
            page = 1 if 'page=1&' in url else 2
            return json.dumps({"success":True,"data":{"nodes":[node(str(page),"dj set")],
                               "pageInfo":{"totalPages":2,"hasNextPage":page==1}}})
        result = collect_hango(SOURCE["canal"], BeautifulSoup(html,"lxml"), fetch)
        self.assertTrue(result.complete_snapshot)
        self.assertEqual(len(result.events), 2)
        self.assertEqual(len(calls), 3)
        self.assertTrue(all('/external/' in u for u in calls))
        with patch('hango_adapter.MAX_PAGES',1):
            limited = collect_hango(SOURCE["canal"],BeautifulSoup(html,"lxml"),fetch)
        self.assertFalse(limited.complete_snapshot)

    def test_wrong_identity_is_not_attributed_to_the_venue(self):
        html = '<iframe src="https://backoffice.hango.ch/external/widgets/estb_live_test"></iframe>'
        with self.assertRaises(ValueError):
            collect_hango(SOURCE["canal"], BeautifulSoup(html,"lxml"), lambda *args,**kw:json.dumps({"success":True,"data":{"name":"Autre établissement"}}))
