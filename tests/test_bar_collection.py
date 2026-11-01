"""Synthetic regression cases; no test event is a real programme listing."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

import agenda
import bar_adapters
import collection_quality as quality
import db
import scraper
from config import config

NOW = datetime.fromisoformat("2026-10-16T12:00:00+02:00")


def event(**changes):
    raw = dict(title="Test synthétique", location="Taco’s Bar", municipality="Lausanne",
               event_kind="MusicEvent", event_status="EventScheduled", date="2026-10-17",
               time="21:00", start_at="2026-10-17T21:00:00+02:00",
               evidence_url="https://tacos-bar.ch/events-data.js")
    return {**raw, **changes}


class QualityTest(unittest.TestCase):
    def assess(self, **changes):
        return quality.assess(event(**changes), "https://tacos-bar.ch/events", NOW)

    def test_good_data_stays_pending(self):
        item = self.assess()
        self.assertEqual(item["status"], "candidate")
        self.assertFalse(quality.publicly_visible(item, NOW))

    def test_exclusions_and_away_event(self):
        for changes in [dict(location="Buzz Club"), dict(private=True), dict(commercial_offer=True),
                        dict(programme_summary=True), dict(event_status="EventCancelled")]:
            self.assertEqual(self.assess(**changes)["status"], "excluded")
        self.assertEqual(self.assess(municipality="Ascona")["status"], "review")
        self.assertEqual(self.assess(location="Bibliothèque")["status"], "review")

    def test_no_guessed_times_years_or_categories(self):
        for changes in [dict(start_at="17 octobre"), dict(time=""), dict(event_kind=""),
                        dict(start_at="2026-10-17T21:00:00"), dict(time_role="unverified"),
                        dict(event_status="EventPostponed"), dict(date="2026-10-18")]:
            self.assertEqual(self.assess(**changes)["status"], "review")

    def test_dedupe_uses_venue_and_session(self):
        one = self.assess()["event"]
        two = self.assess(location="Barberousse")["event"]
        three = self.assess(time="22:00", start_at="2026-10-17T22:00:00+02:00")["event"]
        self.assertEqual(len({one["id"], two["id"], three["id"]}), 3)
        self.assertEqual(one["id"], self.assess(title="TEST SYNTHÉTIQUE")["event"]["id"])

    def test_expired_review_and_past_event(self):
        item = self.assess()
        item["status"] = "approved"
        self.assertTrue(quality.publicly_visible(item, NOW))
        self.assertFalse(quality.publicly_visible(item, NOW + timedelta(hours=25)))
        self.assertEqual(self.assess(date="2026-10-15", start_at="2026-10-15T21:00:00+02:00")["status"], "excluded")


class AdapterTest(unittest.TestCase):
    def test_tacos_does_not_guess_closing_offset_at_clock_change(self):
        raw = "window.TACOS_EVENTS=[{date:'2026-10-24',time:'21:00',end:'02:00',title:'Test',tag:'Live'}];"
        [row] = bar_adapters.parse_tacos(raw, "https://tacos-bar.ch/events", "https://tacos-bar.ch/events-data.js")
        self.assertTrue(row["end_unverified"])
        self.assertNotIn("end_at", row)
        self.assertEqual(quality.assess(row,"https://tacos-bar.ch/events",NOW)["reason"], "unverified_end_time")

    def test_json5_without_execution_or_recurring_promotions(self):
        text = """window.TACOS_EVENTS = [ // dated event
          {date:'2026-10-17',time:'21:00',end:'02:00',title:'Test',tag:'Live',},
          {date:'2026-10-20',prive:true},
          {date:'2026-10-22',title:'Annulé',annule:true},
        ];window.TACOS_RECURRING=[{label:'Happy Hour'}];throw Error('must never run');"""
        rows = bar_adapters.parse_tacos(text, "https://tacos-bar.ch/events", "https://tacos-bar.ch/events-data.js")
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["end_at"], "2026-10-18T02:00:00+02:00")
        self.assertTrue(rows[1]["private"])
        self.assertEqual(rows[2]["event_status"], "EventCancelled")

    def test_extra_concat_is_supported(self):
        rows = bar_adapters.tacos_array('window.TACOS_EVENTS=(window.TACOS_EVENTS||[]).concat([{"title":"Test"}]);')
        self.assertEqual(rows, [{"title": "Test"}])

    def test_captain_promotions_summary_and_uncertain_opening_hour(self):
        rows = bar_adapters.parse_captain(json.dumps([
            dict(title="Test", category="Promo"), dict(title="Test 2", type="Programe"),
            dict(title="Test 3", start="2026-10-17T17:00:00+02:00")]),
            "https://captaincook.ch/", "https://captaincook.ch/events.php")
        self.assertTrue(rows[0]["commercial_offer"])
        self.assertTrue(rows[1]["programme_summary"])
        self.assertEqual(rows[2]["time_role"], "unverified")

    def test_jsonld_nested_itemlist_and_provenance(self):
        raw = {"@type":"ItemList", "itemListElement":[{"item":{
            "@type":"MusicEvent", "name":"Test", "startDate":"2026-10-17T21:00:00+02:00",
            "eventStatus":"https://schema.org/EventCancelled"}}]}
        [row] = scraper._extract_jsonld_events(scraper.BeautifulSoup(
            '<script type="application/ld+json">'+json.dumps(raw)+'</script>', "lxml"), "https://example.test/event")
        self.assertEqual(row["event_status"], "EventCancelled")
        self.assertEqual(row["evidence_url"], "https://example.test/event")

    def test_consolidated_sources_are_broader_than_bars(self):
        self.assertGreater(len(config.SCRAPE_SOURCES), 7)
        self.assertIn("https://www.docks.ch/programme/", config.SCRAPE_SOURCES)
        self.assertIn("https://www.jumeaux.club/", config.SCRAPE_SOURCES)
        self.assertFalse(any("mcba" in u or "bibliotheque" in u or "buzz" in u for u in config.SCRAPE_SOURCES))


class PersistenceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.patch = patch.object(db, "DB_PATH", self.temp.name + "/test.db")
        self.patch.start()
        db.init_db()

    def tearDown(self):
        self.patch.stop()
        self.temp.cleanup()

    def test_approval_changed_data_and_legacy_records(self):
        # Use a future date relative to the real clock to exercise the DB validator.
        start = (datetime.now(agenda.TZ) + timedelta(days=1)).replace(hour=21, minute=0)
        raw = event(start_at=start.isoformat(), date=start.date().isoformat(), time=start.strftime("%H:%M"))
        source = "https://example.test/programme"
        item = quality.assess(raw, source)
        db.bulk_upsert([dict(id="old", title="Old institution", date=raw["date"])])
        db.stage_collection(item)
        self.assertEqual(db.list_public_events(), [])
        db.approve_collection(item["event"]["id"])
        self.assertEqual(len(db.list_public_events()), 1)
        db.stage_collection(quality.assess(raw, source))
        self.assertEqual(len(db.list_public_events()), 1)
        db.stage_collection(quality.assess({**raw, "end_at": (start+timedelta(hours=2)).isoformat()}, source))
        self.assertEqual(db.list_public_events(), [])

    def test_collect_never_auto_publishes(self):
        with patch.object(scraper, "scrape_one", return_value=([event()], "json-ld")):
            scraper.scrape_sources(["https://example.test/programme"])
        self.assertEqual(len(db.collection_items()), 1)
        self.assertEqual(db.list_public_events(), [])

    def test_flask_empty_response_contains_no_demo_or_legacy_events(self):
        import app
        with patch.object(app, "maybe_refresh_from_scraper"):
            response = app.create_app().test_client().get("/api/events").get_json()
        self.assertFalse(response["demo"])
        self.assertEqual(response["events"], [])


class NightTest(unittest.TestCase):
    def test_after_midnight_is_same_night_until_six(self):
        raw = event(id="late", date="2026-10-17", time="01:00", start_at="2026-10-17T01:00:00+02:00",
                    end_at="2026-10-17T04:00:00+02:00")
        for now in ["2026-10-16T18:00:00+02:00", "2026-10-17T02:00:00+02:00"]:
            p = agenda.build_night_programme([raw], datetime.fromisoformat(now))
            self.assertEqual(p["moments"][0]["days"][0]["ids"], ["late"])
        p = agenda.build_night_programme([raw], datetime.fromisoformat("2026-10-17T06:00:00+02:00"))
        self.assertEqual(p["moments"][0]["count"], 0)
