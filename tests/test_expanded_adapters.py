import threading
import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from expanded_adapters import parse_folklor, parse_cityclub, parse_naftule, parse_boulimie, parse_arsenic, parse_mad_ticket, parse_pulloff, collect_grange, collect_lagenda, parse_lagenda, collect_expanded
from samstag.collection.adapters.arsenic import parse_arsenic as packaged_parse_arsenic
from samstag.collection.adapters.boulimie import parse_boulimie as packaged_parse_boulimie
from samstag.collection.adapters.cityclub import parse_cityclub as packaged_parse_cityclub
from samstag.collection.adapters.naftule import parse_naftule as packaged_parse_naftule
from samstag.collection.adapters.grange import collect_grange as packaged_collect_grange
from samstag.collection.adapters.pulloff import parse_pulloff as packaged_parse_pulloff
from samstag.collection.adapters.folklor import parse_folklor as packaged_parse_folklor
from samstag.collection.adapters.mad import parse_mad_ticket as packaged_parse_mad_ticket
from samstag.collection.adapters.lagenda import collect_lagenda as packaged_collect_lagenda, parse_lagenda as packaged_parse_lagenda
from collection_worker import serve


def soup(value):
    return BeautifulSoup(value, "lxml")


class ExpandedReadersTest(unittest.TestCase):
    def test_lagenda_legacy_imports_are_packaged_adapters(self):
        self.assertIs(parse_lagenda, packaged_parse_lagenda)
        self.assertIs(collect_lagenda, packaged_collect_lagenda)

    def test_cityclub_legacy_import_is_the_packaged_adapter(self):
        self.assertIs(parse_cityclub, packaged_parse_cityclub)

    def test_naftule_and_boulimie_legacy_imports_are_packaged_adapters(self):
        self.assertIs(parse_naftule, packaged_parse_naftule)
        self.assertIs(parse_boulimie, packaged_parse_boulimie)

    def test_arsenic_legacy_import_is_the_packaged_adapter(self):
        self.assertIs(parse_arsenic, packaged_parse_arsenic)

    def test_grange_and_pulloff_legacy_imports_are_packaged_adapters(self):
        self.assertIs(collect_grange, packaged_collect_grange)
        self.assertIs(parse_pulloff, packaged_parse_pulloff)

    def test_folklor_and_mad_legacy_imports_are_packaged_adapters(self):
        self.assertIs(parse_folklor, packaged_parse_folklor)
        self.assertIs(parse_mad_ticket, packaged_parse_mad_ticket)

    def test_arsenic_preserves_occurrences_nohour_cancellation_and_evidence(self):
        page = '''<script>var spectacles = [{
            "auteur": "DJ &amp; Test", "title": "Soirée &amp; amis",
            "description": "DJ sets &amp; performance", "link": "https://arsenic.ch/spectacle/test",
            "dates": ["2026-11-10 22:30", "2026-11-11 00:00"], "nohour": ["2026-11-11"],
            "img": {"src": "https://arsenic.ch/image.jpg"}, "gratuit": 1, "canceled": true
        }];</script>'''
        first, second = parse_arsenic(soup(page), 'https://arsenic.ch/')
        self.assertEqual(
            {key: first[key] for key in (
                'title', 'url', 'evidence_url', 'location', 'municipality',
                'event_kind', 'category', 'adapter', 'date', 'time',
                'start_at', 'description', 'image', 'price', 'event_status',
            )},
            {
                'title': 'DJ & Test — Soirée & amis',
                'url': 'https://arsenic.ch/spectacle/test',
                'evidence_url': 'https://arsenic.ch/', 'location': 'Arsenic',
                'municipality': 'Lausanne', 'event_kind': 'ClubNight',
                'category': 'Clubbing', 'adapter': 'official-programme-v3',
                'date': '2026-11-10', 'time': '22:30',
                'start_at': '2026-11-10T22:30:00+01:00',
                'description': 'DJ sets & performance',
                'image': 'https://arsenic.ch/image.jpg', 'price': 'Gratuit',
                'event_status': 'EventCancelled',
            },
        )
        self.assertEqual((second['date'], second['time']), ('', ''))
        self.assertNotIn('start_at', second)
        self.assertNotIn('source_event_key', first)

    def test_arsenic_classification_and_invalid_calendar(self):
        page = '''<script>var spectacles = [
            {"title":"Danse", "description":"Création danse", "dates":["2026-11-12 19:00"]},
            {"title":"Scène", "description":"Performance théâtre", "dates":["date inconnue"]},
            "entrée invalide"
        ];</script>'''
        dance, theatre = parse_arsenic(soup(page), 'https://arsenic.ch/')
        self.assertEqual((dance['event_kind'], dance['category']), ('DanceEvent', 'Danse'))
        self.assertEqual((theatre['event_kind'], theatre['category'], theatre['date']), ('TheaterEvent', 'Théâtre', ''))
        with self.assertRaises(ValueError):
            parse_arsenic(soup('<h1>Maintenance</h1>'), 'https://arsenic.ch/')
        with self.assertRaises(ValueError):
            parse_arsenic(soup('<script>var spectacles = {}</script>'), 'https://arsenic.ch/')

    def test_pulloff_cross_year_schedule_only_uses_published_weekdays(self):
        page = '<div class="siteorigin-widget-tinymce"><h1>Test</h1><h2>30.12 — 03.01.2027</h2><p>me/je: 20h30</p></div>'
        rows = parse_pulloff(soup(page), 'https://www.pulloff.ch/test/')
        self.assertEqual([(r['date'], r['time']) for r in rows], [('2026-12-30','20:30'),('2026-12-31','20:30')])

    def test_grange_music_and_truncation(self):
        card = '<a class="card" href="/test"><div class="event-card-title">Concert</div><div class="list-inline">Musique</div><div class="card-footer">16.10.2026</div></a>'
        detail = '<div class="event-right-content"><div class="border-bottom"><p>Ve 16.10, 20h30</p></div><div class="border-bottom"><p>&gt; La Grange</p></div></div>'
        with patch('samstag.collection.adapters.grange.config', MAX_DETAIL_PAGES=1):
            result = collect_grange(soup(card*2), 'https://grange-unil.ch/', Mock(return_value=detail))
        self.assertTrue(result.partial)
        self.assertEqual(result.events[0]['category'], 'Musique')
        self.assertEqual(result.events[0]['date'], '2026-10-16')

    def test_lagenda_reports_pagination_limit(self):
        form = soup('<form class="em-search-form"><select name="category[]"><option value="1">Musique</option></select></form>')
        listing = '<div class="em-pagination"><a title="suite">5</a><a title="suite">2</a><a title="suite">3</a><a title="suite">4</a></div>'
        with patch('samstag.collection.adapters.lagenda.parse_lagenda', return_value=[]), patch('samstag.collection.adapters.lagenda.config', MAX_AGENDA_PAGES=4, COLLECTION_HORIZON_DAYS=90):
            result = collect_lagenda(form, 'https://l-agenda.ch/', Mock(return_value=listing))
        self.assertTrue(result.partial)

    def test_folklor_keeps_year_and_midnight_and_does_not_invent_missing_time(self):
        page = '<div id="program"><article class="event"><div class="event-title">Test</div><div class="event-date">24.10.2026</div><div class="event-time">23:59</div></article></div>'
        [row] = parse_folklor(soup(page), 'https://www.folklor.club/events/')
        self.assertEqual(row['start_at'], '2026-10-24T23:59:00+02:00')
        [row] = parse_folklor(soup(page.replace('23:59','')), 'https://www.folklor.club/events/')
        self.assertNotIn('start_at', row)
        with self.assertRaises(ValueError):
            parse_folklor(soup('<h1>Site en maintenance</h1>'), 'https://www.folklor.club/events/')

    def test_cityclub_sessions_keep_their_year_and_identity_across_new_year(self):
        page = '''<div class="action" data-idaction="1"><h4>Film 1971</h4>
            <img class="localVignette" src="/images/film.jpg"><div class="description">Présentation officielle</div>
            <div class="projections"><a href="https://cityclub.ticketack.com/screening/buy/a">ve 31.12 / 20h30</a>
            <a href="https://cityclub.ticketack.com/screening/buy/b">sa 1.1 / 18h</a>
            <a href="https://cityclub.ticketack.com/screening/buy/ignored">di 2.3 / 17h</a></div></div>'''
        a,b = parse_cityclub(soup(page), 'https://www.cityclubpully.ch/affiche/2026-12-00')
        self.assertEqual((a['date'],b['date']), ('2026-12-31','2027-01-01'))
        self.assertNotEqual(a['source_event_key'], b['source_event_key'])
        self.assertEqual(
            {key: a[key] for key in (
                'title', 'url', 'evidence_url', 'location', 'municipality',
                'event_kind', 'category', 'adapter', 'date', 'time',
                'start_at', 'description', 'image', 'source_event_key',
            )},
            {
                'title': 'Film 1971',
                'url': 'https://cityclub.ticketack.com/screening/buy/a',
                'evidence_url': 'https://www.cityclubpully.ch/affiche/2026-12-00',
                'location': 'Cinéma CityClub', 'municipality': 'Pully',
                'event_kind': 'ScreeningEvent', 'category': 'Cinéma',
                'adapter': 'official-programme-v3', 'date': '2026-12-31',
                'time': '20:30', 'start_at': '2026-12-31T20:30:00+01:00',
                'description': 'Présentation officielle',
                'image': 'https://www.cityclubpully.ch/images/film.jpg',
                'source_event_key': 'https://cityclub.ticketack.com/screening/buy/a',
            },
        )

    def test_cityclub_rejects_a_page_without_a_monthly_programme(self):
        with self.assertRaises(ValueError):
            parse_cityclub(soup('<h1>Maintenance</h1>'), 'https://www.cityclubpully.ch/')

    def test_naftule_separates_performances_on_same_ticket_page(self):
        card = '''<li data-show="test" data-genres="humour"><span>20H30</span>
            <h3><a href="https://monbillet.ch/events/test">Spectacle</a></h3>
            <img src="/images/spectacle.jpg"></li>'''
        page = ''.join('<div data-day-panel data-day="'+day+'">'+card+'</div>' for day in ['2026-11-14','2026-11-15'])
        a,b = parse_naftule(soup(page), 'https://naftule.ch/programme/')
        self.assertNotEqual(a['date'],b['date'])
        self.assertNotIn('source_event_key', a)
        self.assertEqual(
            {key: a[key] for key in (
                'title', 'url', 'evidence_url', 'location', 'municipality',
                'event_kind', 'category', 'adapter', 'date', 'time',
                'start_at', 'image',
            )},
            {
                'title': 'Spectacle', 'url': 'https://monbillet.ch/events/test',
                'evidence_url': 'https://naftule.ch/programme/',
                'location': 'Pavillon Naftule', 'municipality': 'Lausanne',
                'event_kind': 'ComedyEvent', 'category': 'Humour',
                'adapter': 'official-programme-v3', 'date': '2026-11-14',
                'time': '20:30', 'start_at': '2026-11-14T20:30:00+01:00',
                'image': 'https://naftule.ch/images/spectacle.jpg',
            },
        )

    def test_naftule_keeps_ambiguous_hours_unverified_and_rejects_missing_calendar(self):
        page = '''<div data-day-panel data-day="2026-11-14"><li data-show="test" data-genres="musique-et-chant">
            <span>18h</span><span>20h30</span><h3>Deux horaires</h3></li></div>'''
        [row] = parse_naftule(soup(page), 'https://naftule.ch/programme/')
        self.assertEqual((row['event_kind'], row['category'], row['time']), ('MusicEvent', 'Musique', ''))
        self.assertNotIn('start_at', row)
        with self.assertRaises(ValueError):
            parse_naftule(soup('<h1>Maintenance</h1>'), 'https://naftule.ch/programme/')

    def test_boulimie_uses_only_explicit_weekday_schedule(self):
        page = '''<h1 class="show-artist">Artiste</h1><h2 class="show-title">Spectacle</h2>
            <div class="show-schedule">4 au 14 novembre 2026</div><div class="normal-text">
            <p>Présentation officielle</p><h6>Mercredi et jeudi: 19h<br>Vendredi: 20h<br>Samedi: 17h</h6></div>'''
        rows = parse_boulimie(soup(page), 'https://theatreboulimie.com/spectacle/test/')
        self.assertEqual([r['date'] for r in rows], ['2026-11-04','2026-11-05','2026-11-06','2026-11-07','2026-11-11','2026-11-12','2026-11-13','2026-11-14'])
        self.assertEqual(rows[0]['time'], '19:00')
        self.assertEqual(
            {key: rows[0][key] for key in (
                'title', 'url', 'evidence_url', 'location', 'municipality',
                'event_kind', 'category', 'adapter', 'start_at', 'description',
            )},
            {
                'title': 'Artiste — Spectacle',
                'url': 'https://theatreboulimie.com/spectacle/test/',
                'evidence_url': 'https://theatreboulimie.com/spectacle/test/',
                'location': 'Théâtre Boulimie', 'municipality': 'Lausanne',
                'event_kind': 'ComedyEvent', 'category': 'Humour',
                'adapter': 'official-programme-v3',
                'start_at': '2026-11-04T19:00:00+01:00',
                'description': 'Présentation officielle Mercredi et jeudi: 19h Vendredi: 20h Samedi: 17h',
            },
        )
        [row] = parse_boulimie(soup(page.replace('<h6>','Ces soirées n\'ont pas lieu à Boulimie<h6>')), 'https://theatreboulimie.com/spectacle/test/')
        self.assertEqual(row['location'], '')

    def test_boulimie_single_date_and_missing_explicit_hour_stay_in_review(self):
        page = '''<h1 class="show-artist">Test</h1><div class="show-schedule">14 novembre 2026</div>
            <div class="normal-text"><p>Horaire non publié</p></div>'''
        [row] = parse_boulimie(soup(page), 'https://theatreboulimie.com/spectacle/test/')
        self.assertEqual((row['date'], row['time']), ('', ''))
        self.assertNotIn('start_at', row)

    def test_mad_reads_product_doors_but_rejects_offsite_and_unrelated_footer_time(self):
        page = '<div class="product"><h1 class="product_title">Ticket: Test, Vendredi 16 oct 2026</h1><p>MAD Mainfloor</p><p>Ouverture des portes 23h00</p></div><footer>Autre soirée 21h</footer>'
        [row] = parse_mad_ticket(soup(page), 'https://www.mad-shop.ch/?product=ticket-test')
        self.assertEqual((row['time'],row['time_role']), ('23:00','doors'))
        [row] = parse_mad_ticket(soup(page.replace('Test,','Montreux,')), 'https://www.mad-shop.ch/?product=ticket-test')
        self.assertEqual(row['location'], '')

    def test_mad_all_failed_details_are_an_error_not_an_empty_calendar(self):
        agenda = soup('''<section><h3>6 novembre 2026</h3><h3>Soirée</h3>
            <a href="https://www.mad-shop.ch/?product=ticket-test">Billets</a></section>''')
        result = collect_expanded(
            'https://www.mad.club/agenda/', agenda,
            Mock(side_effect=RuntimeError('offline')),
        )
        self.assertTrue(result.partial)
        self.assertEqual(result.parse_status, 'error')
        self.assertEqual((result.pages_expected, result.pages_read), (1, 0))
        self.assertEqual(result.events, [])


class WorkerTest(unittest.TestCase):
    def test_failure_waits_and_then_retries_until_stop(self):
        stop = Mock()
        stop.is_set.side_effect = [False,False,True]
        cycle = Mock(side_effect=[RuntimeError('synthetic outage'),{'status':'ok'}])
        with self.assertLogs('collection_worker', level='INFO'):
            serve(60, stop, cycle)
        self.assertEqual(cycle.call_count, 2)
        self.assertEqual(stop.wait.call_count, 2)

    def test_stopped_worker_does_not_start_and_short_interval_is_rejected(self):
        stop = threading.Event();stop.set()
        cycle = Mock()
        serve(60, stop, cycle)
        cycle.assert_not_called()
        with self.assertRaises(ValueError):
            serve(0, stop, cycle)
