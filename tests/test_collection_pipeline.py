"""Synthetic DOM regressions for the inspected adapters and publication rules."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from bs4 import BeautifulSoup

import agenda
import collection_quality as quality
import db
import scraper
from collection_result import CollectionResult
from venue_adapters import parse_docks, parse_jumeaux, parse_tourisme, parse_dclub, parse_chorus, parse_bellevaux, set_start
from samstag.collection.adapters.dclub import parse_dclub as packaged_parse_dclub
from samstag.collection.adapters.docks import parse_docks as packaged_parse_docks
from samstag.collection.adapters.docks_romandie import collect_docks_romandie
from samstag.collection.adapters.bellevaux import parse_bellevaux as packaged_parse_bellevaux
from samstag.collection.adapters.chorus import parse_chorus as packaged_parse_chorus
from samstag.collection.adapters.jumeaux import parse_jumeaux as packaged_parse_jumeaux
from samstag.collection.adapters.tourisme import parse_tourisme as packaged_parse_tourisme
from tests.test_bar_collection import event, NOW


def soup(html):
    return BeautifulSoup(html, "lxml")


class ReaderTest(unittest.TestCase):
    def test_tourisme_legacy_import_uses_packaged_adapter(self):
        self.assertIs(parse_tourisme, packaged_parse_tourisme)

    def test_jumeaux_chorus_bellevaux_legacy_imports_use_packaged_adapters(self):
        self.assertIs(parse_jumeaux, packaged_parse_jumeaux)
        self.assertIs(parse_chorus, packaged_parse_chorus)
        self.assertIs(parse_bellevaux, packaged_parse_bellevaux)

    def test_docks_romandie_dclub_legacy_imports_use_packaged_adapters(self):
        from venue_adapters import collect_dclub, collect_docks_romandie as legacy_collect_docks_romandie

        from samstag.collection.adapters.dclub import collect_dclub as packaged_collect_dclub

        self.assertIs(parse_docks, packaged_parse_docks)
        self.assertIs(parse_dclub, packaged_parse_dclub)
        self.assertIs(collect_dclub, packaged_collect_dclub)
        self.assertIs(legacy_collect_docks_romandie, collect_docks_romandie)

    def test_docks_detail_failures_report_all_failed_and_partial_passes(self):
        from venue_adapters import collect_venue
        day = datetime.now(agenda.TZ).date() + timedelta(days=3)
        urls = [f"https://www.docks.ch/evenement/concerts/{day:%Y%m%d}/test-{i}/" for i in (1, 2)]
        listing = soup("".join(f'<a href="{url}">Concert</a>' for url in urls))
        detail = '''<h1>Concert de test</h1><span class="event-info-date">{day}</span>
        <span class="event-info-door"><span class="event-info-label">Début</span>20:30</span>'''.format(day=day.strftime('%d.%m.%Y'))
        all_failed = collect_venue(
            "https://www.docks.ch/programme/", listing,
            lambda _: (_ for _ in ()).throw(scraper.FetchError("offline")),
        )
        self.assertTrue(all_failed.partial)
        self.assertEqual((all_failed.pages_expected, all_failed.pages_read), (2, 0))
        self.assertEqual(all_failed.parse_status, "error")
        partial = collect_venue(
            "https://www.docks.ch/programme/", listing,
            lambda url: detail if url == urls[0] else (_ for _ in ()).throw(scraper.FetchError("offline")),
        )
        self.assertEqual(len(partial.events), 1)
        self.assertEqual((partial.pages_expected, partial.pages_read), (2, 1))
        self.assertEqual(partial.parse_status, "partial")

    def test_romandie_jsonld_keeps_doors_role_and_dj_classification(self):
        from venue_adapters import collect_venue

        target = "https://leromandie.ch/event/test-event/"
        listing = soup(f'<a href="{target}">Événement</a>')
        detail = '''<script type="application/ld+json">{
          "@context":"https://schema.org", "@type":"MusicEvent",
          "name":"Soirée synthétique", "startDate":"2026-11-13T22:00:00+01:00",
          "url":"https://leromandie.ch/event/test-event/",
          "location":{"@type":"Place", "name":"Le Romandie", "address":"Lausanne"}
        }</script><h2>DJ</h2>'''
        result = collect_venue("https://leromandie.ch/programme", listing, lambda _: detail)

        self.assertFalse(result.partial)
        self.assertEqual((result.pages_expected, result.pages_read), (1, 1))
        [row] = result.events
        self.assertEqual(row["adapter"], "romandie-jsonld-v1")
        self.assertEqual(row["time_role"], "doors")
        self.assertEqual((row["event_kind"], row["category"]), ("ClubNight", "Clubbing"))

    def test_cinema_separates_sessions_and_uses_programme_year_not_film_year(self):
        html = '''<div class="block-default"><div class="block-default-overtitle">Di 18.10 à 20:45 | Ma 20.10 à 20:30</div>
        <div class="block-default-header"><a href="https://www.cinemabellevaux.ch/14-10-20-10-2026/test"><h3>Film synthétique</h3></a><span class="visible-xs">Réalisation 1971</span></div></div>'''
        rows = parse_bellevaux(soup(html), "https://www.cinemabellevaux.ch/")
        self.assertEqual([(r["date"],r["time"]) for r in rows], [('2026-10-18','20:45'),('2026-10-20','20:30')])
        self.assertNotEqual(quality.assess(rows[0],"https://www.cinemabellevaux.ch/",NOW)["event"]["id"],quality.assess(rows[1],"https://www.cinemabellevaux.ch/",NOW)["event"]["id"])
        self.assertEqual(parse_bellevaux(soup(html.replace('14-10-20-10-2026','14-10-20-10')), "https://www.cinemabellevaux.ch/"), [])
        self.assertEqual(parse_bellevaux(soup(html.replace('18.10','22.10').replace('20.10','23.10')), "https://www.cinemabellevaux.ch/"), [])

    def test_chorus_requires_published_month_and_year(self):
        html = '''<section class="menu_page"><h2 class="section_title">PROGRAMME OCTOBRE 2026</h2>
        <div class="our_event_list"><div class="day_month">23 oct</div><div class="eventtexttitle"><a href="/event/test">Concert synthétique</a></div>
        <div class="event_time">21:00</div><div class="event_location">Entrée libre</div><div class="event_buyticket">Complet</div></div></section>'''
        [row] = parse_chorus(soup(html), "https://chorus.ch/")
        self.assertEqual(row["date"], '2026-10-23')
        self.assertEqual(row["time"], '21:00')
        self.assertEqual(row["availability"], 'sold_out')
        self.assertEqual(row["price"], 'Entrée libre')
        self.assertEqual(parse_chorus(soup(html.replace('OCTOBRE 2026','OCTOBRE')), "https://chorus.ch/"), [])

    def test_dclub_rooms_and_doors_are_kept_distinct(self):
        html = '''<div class="event" data-date="20261017" data-place='["d-club"]' data-styles='["electronic"]'>
        <a class="main" href="https://dclub.ch/agenda/20261017/test#d-club"><header class="dtitle">Soirée de test</header><div class="header"><span class="name">DJ test</span></div></a>
        <p class="door">Porte: 23:00</p></div>'''
        [row] = parse_dclub(soup(html), "https://dclub.ch/agenda/")
        self.assertEqual(row["time_role"], "doors")
        self.assertEqual(row["event_kind"], "ClubNight")
        self.assertEqual(row["time"], "23:00")
        self.assertTrue(row["source_event_key"].endswith('#d-club'))
        self.assertEqual(quality.assess(row,"https://dclub.ch/agenda/",NOW)["status"], "candidate")
        [concert] = parse_dclub(soup(html.replace('electronic','concert')), "https://dclub.ch/agenda/")
        self.assertEqual(quality.assess(concert,"https://dclub.ch/agenda/",NOW)["reason"], "doors_not_artistic_start")
        [room] = parse_dclub(soup(html.replace('d-club','abc')), "https://dclub.ch/agenda/")
        self.assertEqual(quality.assess(room,"https://dclub.ch/agenda/",NOW)["status"], "review")

    def test_navigation_cards_without_a_real_date_are_discarded(self):
        self.assertIsNone(scraper._parse_card(soup('<article><h2>Événements</h2><a href="/events">Agenda</a></article>').article,"https://example.test"))

    def test_docks_uses_artistic_start_not_doors(self):
        html = '''<h1>Concert de test</h1><span class="event-info-date">17.10.2026</span>
        <span class="event-info-door"><span class="event-info-label">Portes</span>19:00</span>
        <span class="event-info-door"><span class="event-info-label">Début</span>20:30</span>'''
        row = parse_docks(soup(html), "https://www.docks.ch/evenement/concerts/20261017/test/")
        self.assertEqual(row["time"], "20:30")
        self.assertEqual(row["doors_time"], "19:00")
        self.assertEqual(row["start_at"], "2026-10-17T20:30:00+02:00")
        [missing] = [parse_docks(soup(html.replace("Début", "Fin")), "https://www.docks.ch/test")]
        self.assertNotIn("start_at", missing)

    def test_jumeaux_ignores_hidden_cancelled_and_free_flags(self):
        html = '''<div class="nextevent"><h2 class="event__title">Concert de test</h2>
        <div class="concert__date">17/10/2026</div>
        <div class="nextevent__alert w-condition-invisible">Annulé</div>
        <div class="event__number w-condition-invisible">Entrée Libre</div>
        <div class="concert__detail">Tarif normal <div>30</div> CHF</div>
        <div class="concert__detail">Portes <div>19h</div> / Concert <div>20h30</div></div>
        <a href="/evenements/test">Voir plus</a></div>'''
        [row] = parse_jumeaux(soup(html), "https://www.jumeaux.club/")
        self.assertEqual(row["price"], "CHF 30")
        self.assertNotIn("event_status", row)
        self.assertEqual(row["time"], "20:30")
        [cancelled] = parse_jumeaux(soup(html.replace('nextevent__alert w-condition-invisible','nextevent__alert')), "https://www.jumeaux.club/")
        self.assertEqual(cancelled["event_status"], "EventCancelled")

    def test_tourism_overnight_single_occurrence_and_actual_address(self):
        hours = json.dumps({"openings": [{"day": 4,"from":"2030","until":"2359"},
                                         {"day":5,"from":"0000","until":"0100"}]})
        html = '''<h1 class="hero__title">Concert de test</h1><div class="hero__tags">Musique</div>
        <span class="gmtLocationSingle">Barberousse</span><span class="gmtDateSingle">Le 05.11.2026</span>
        <div class="tabs__content-item"><div class="address">Barberousse<br>Rue de Genève 17<br>1003 Lausanne<p>Comment s'y rendre</p></div></div>
        <div class="js-openingHours" data-opening='{hours}'></div>
        <footer>Administration, 1001 Lausanne</footer>'''.replace('{hours}', hours)
        row = parse_tourisme(soup(html), "https://www.lausanne-tourisme.ch/fr/evenement/test/")
        self.assertEqual(row["start_at"], "2026-11-05T20:30:00+01:00")
        self.assertEqual(row["end_at"], "2026-11-06T01:00:00+01:00")
        self.assertEqual(row["municipality"], "Lausanne")
        self.assertNotIn("Administration", row["address"])
        multi = parse_tourisme(soup(html.replace('Le 05.11.2026','Du 05.11.2026 au 10.11.2026')), "https://example.test")
        self.assertNotIn("start_at", multi)

    def test_unknown_and_ambiguous_local_clocks_are_not_invented(self):
        from datetime import date, time
        for day in [date(2026,3,29), date(2026,10,25)]:
            row = {}
            set_start(row, day, time(2,30))
            self.assertNotIn("start_at", row)

    def test_neighbouring_town_screening_daytime_and_excluded_venue(self):
        row = event(location="Cinéma CityClub", municipality="Pully", event_kind="ScreeningEvent")
        self.assertEqual(quality.assess(row, "https://example.test", NOW)["status"], "candidate")
        row.update(time="14:00", start_at="2026-10-17T14:00:00+02:00")
        self.assertEqual(quality.assess(row, "https://example.test", NOW)["status"], "candidate")
        row.update(location="Bibliothèque Chauderon")
        self.assertEqual(quality.assess(row, "https://example.test", NOW)["status"], "excluded")


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path_patch = patch.object(db, "DB_PATH", self.directory.name+"/events.db")
        self.path_patch.start()
        db.init_db()
        start = (datetime.now(agenda.TZ)+timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
        self.raw = event(date=start.date().isoformat(), time="21:00", start_at=start.isoformat())

    def tearDown(self):
        self.path_patch.stop()
        self.directory.cleanup()

    def test_daytime_session_is_published_and_appears_in_today_programme(self):
        start = (datetime.now(agenda.TZ)+timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
        raw = {**self.raw, 'time':'14:00', 'start_at':start.isoformat()}
        db.stage_collection(quality.assess(raw, 'https://tacos-bar.ch/events'))
        [published] = db.list_public_events()
        programme = agenda.build_night_programme([published], start.replace(hour=9))
        self.assertEqual(programme['moments'][0]['days'][0]['ids'], [published['id']])

    def test_qualified_source_auto_publishes_then_cancelled_disappears(self):
        source = "https://tacos-bar.ch/events"
        db.stage_collection(quality.assess(self.raw, source))
        self.assertEqual(len(db.list_public_events()), 1)
        db.stage_collection(quality.assess({**self.raw, "event_status":"EventCancelled"}, source))
        self.assertEqual(db.list_public_events(), [])

    def test_official_record_wins_but_aggregator_proof_is_retained(self):
        official = "https://tacos-bar.ch/events"
        aggregator = "https://www.lausanne-tourisme.ch/fr/evenement/"
        db.stage_collection(quality.assess(self.raw, official))
        db.stage_collection(quality.assess({**self.raw, "description":"Autre description"}, aggregator))
        [published] = db.list_public_events()
        self.assertEqual(published["source_url"], official)
        self.assertIn(aggregator, published["evidence_urls"])
        self.assertEqual(len(db.collection_items()), 1)

    def test_corrected_hour_supersedes_previous_session_without_revival(self):
        source = "https://tacos-bar.ch/events"
        raw = {**self.raw, "source_event_key":"https://example.test/dedicated-event"}
        db.stage_collection(quality.assess(raw, source))
        changed = {**raw, "time":"22:00", "start_at":raw["start_at"].replace("T21:","T22:")}
        db.stage_collection(quality.assess(changed, source))
        self.assertEqual([e["time"] for e in db.list_public_events()], ["22:00"])
        db.stage_collection(quality.assess(raw, "https://www.lausanne-tourisme.ch/fr/evenement/"))
        self.assertEqual([e["time"] for e in db.list_public_events()], ["22:00"])

    def test_shared_calendar_does_not_supersede_distinct_occurrences(self):
        source = "https://tacos-bar.ch/events"
        db.stage_collection(quality.assess(self.raw, source))
        changed = {**self.raw, "time":"22:00", "start_at":self.raw["start_at"].replace("T21:","T22:")}
        db.stage_collection(quality.assess(changed, source))
        self.assertEqual(len(db.list_public_events()), 2)

    def test_shared_lease_and_release_after_failure(self):
        with self.assertRaises(RuntimeError):
            with db.collection_lease() as first:
                self.assertTrue(first)
                with db.collection_lease() as second:
                    self.assertFalse(second)
                raise RuntimeError("synthetic error")
        with db.collection_lease() as third:
            self.assertTrue(third)

    def test_two_complete_snapshots_required_to_withdraw_and_reappearance_restores(self):
        source = "https://tacos-bar.ch/events"
        item = quality.assess(self.raw, source)
        db.stage_collection(item)
        db.reconcile_source_snapshot(source, set())
        self.assertEqual(len(db.list_public_events()), 1)
        db.reconcile_source_snapshot(source, set())
        self.assertEqual(db.list_public_events(), [])
        db.stage_collection(quality.assess(self.raw, "https://www.lausanne-tourisme.ch/fr/evenement/"))
        self.assertEqual(db.list_public_events(), [])
        db.stage_collection(quality.assess(self.raw, source))
        db.reconcile_source_snapshot(source, {item["event"]["id"]})
        self.assertEqual(len(db.list_public_events()), 1)

    def test_one_broken_parser_does_not_stop_other_sources(self):
        def collect(url):
            if url == "https://example.test/broken":
                raise ValueError("structure changed")
            return [self.raw], "synthetic"
        with patch.object(scraper, "scrape_one", side_effect=collect):
            result = scraper.scrape_sources(["https://example.test/broken", "https://tacos-bar.ch/events"])
        self.assertEqual(len(result), 1)
        self.assertEqual(len(db.list_public_events()), 1)
        self.assertEqual({s["status"] for s in db.source_status()}, {"ok","error"})

    def test_every_active_channel_gets_four_dimension_diagnostic(self):
        from source_registry import active_sources
        with patch.object(scraper, "scrape_one", return_value=CollectionResult([], "synthetic")):
            scraper.scrape_sources()
        rows = db.source_run_diagnostics()
        self.assertEqual({row["source_url"] for row in rows}, {s["canal"] for s in active_sources()})
        self.assertEqual(len(rows), 37)
        for row in rows:
            self.assertEqual(row["access_status"], "ok")
            self.assertEqual(row["parse_status"], "ok")
            self.assertIn(row["completeness_status"], {"unknown", "complete", "partial", "limited"})
            self.assertIn(row["editorial_status"], {"automatic", "review_required"})

    def test_partial_or_malformed_snapshot_never_withdraws_missing_events(self):
        from collection_result import CollectionResult
        url = "https://tacos-bar.ch/events"
        for result in [CollectionResult([], "synthetic", complete_snapshot=True, partial=True),
                       CollectionResult([None], "synthetic", complete_snapshot=True)]:
            with self.subTest(result=result), patch.object(scraper, "scrape_one", return_value=result), patch.object(db, "reconcile_source_snapshot") as reconcile:
                scraper.scrape_sources([url])
                reconcile.assert_not_called()
                self.assertEqual(db.source_status()[0]["status"], "partial")

    def test_flask_returns_collected_events_and_source_automation_status(self):
        import app
        db.stage_collection(quality.assess(self.raw, "https://tacos-bar.ch/events"))
        with patch.object(app, "maybe_refresh_from_scraper"):
            client = app.create_app().test_client()
            payload = client.get("/api/events").get_json()
            self.assertFalse(payload["demo"])
            self.assertEqual(payload["total"], 1)
            diagnostic = client.get("/api/sources").get_json()
            from source_registry import SOURCES
            self.assertEqual(len(diagnostic["sources"]), len(SOURCES))
            self.assertEqual(sum(not s["enabled"] for s in diagnostic["sources"]), 2)
            self.assertTrue(any(s["publication"] == "automatique après contrôles" for s in diagnostic["sources"]))

    def test_worker_reports_missing_and_partial_checks_and_lease_contention(self):
        from collection_worker import run_cycle
        with db.collection_lease() as acquired:
            self.assertTrue(acquired)
            with patch.object(scraper, 'scrape_sources') as collect:
                self.assertEqual(run_cycle()['status'], 'skipped')
                collect.assert_not_called()
        with patch('source_registry.active_sources', return_value=[{'canal':'https://example.test/'}]), patch.object(scraper, 'scrape_sources', return_value=[]):
            self.assertEqual(run_cycle()['status'], 'degraded')
        def partial():
            db.log_scrape('scraper', 'https://example.test/', 'partial', 0, 'truncated')
            return []
        with patch('source_registry.active_sources', return_value=[{'canal':'https://example.test/'}]), patch.object(scraper, 'scrape_sources', side_effect=partial):
            self.assertEqual(run_cycle()['partial'], ['https://example.test/'])

    def test_health_distinguishes_never_collected_fresh_and_stale(self):
        from collection_health import health
        source = {'id':'test','nom':'Test','canal':'https://example.test/','auto_publish':False}
        with patch('collection_health.active_sources', return_value=[source]):
            self.assertEqual(health()['states'], {'never_collected':1})
            db.log_scrape('scraper', source['canal'], 'empty', 0, 'calendar empty')
            self.assertEqual(health()['status'], 'ok')
            self.assertEqual(health(now=db.source_status()[0]['timestamp']+86401)['states'], {'stale':1})

    def test_health_separates_known_limit_from_new_incident(self):
        from collection_health import health
        source = {'id':'test','nom':'Test','canal':'https://example.test/','auto_publish':False}
        run_id = db.start_collection_run(1)
        db.log_source_run(run_id, source['canal'], access_status='ok', parse_status='ok',
                          completeness_status='limited', editorial_status='review_required')
        db.finish_collection_run(run_id, 'ok')
        with patch('collection_health.active_sources', return_value=[source]):
            limited = health()
            self.assertEqual(limited['status'], 'ok')
            self.assertEqual(limited['states'], {'limited':1})
            self.assertEqual(limited['incidents'], [])
            run_id = db.start_collection_run(1)
            db.log_source_run(run_id, source['canal'], access_status='error', parse_status='not_run',
                              completeness_status='unknown', editorial_status='review_required')
            db.finish_collection_run(run_id, 'degraded')
            broken = health()
            self.assertEqual(broken['status'], 'degraded')
            self.assertEqual(broken['incidents'][0]['status'], 'access_error')

    def test_technical_retention_preserves_event_evidence(self):
        source = "https://tacos-bar.ch/events"
        db.stage_collection(quality.assess(self.raw, source))
        db.log_scrape('scraper', source, 'ok', 1, 'old')
        run_id = db.start_collection_run(1)
        with db.get_conn() as conn:
            conn.execute("UPDATE scrape_log SET timestamp=0")
            conn.execute("UPDATE collection_runs SET started_at=0 WHERE run_id=?", (run_id,))
        deleted = db.prune_collection_diagnostics(90)
        self.assertEqual(deleted['scrape_logs'], 1)
        self.assertEqual(deleted['collection_runs'], 1)
        self.assertEqual(len(db.collection_items()), 1)
