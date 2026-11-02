import threading
import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from expanded_adapters import parse_folklor, parse_cityclub, parse_naftule, parse_boulimie, parse_mad_ticket, parse_pulloff, collect_grange, collect_lagenda, collect_expanded
from collection_worker import serve


def soup(value):
    return BeautifulSoup(value, "lxml")


class ExpandedReadersTest(unittest.TestCase):
    def test_pulloff_cross_year_schedule_only_uses_published_weekdays(self):
        page = '<div class="siteorigin-widget-tinymce"><h1>Test</h1><h2>30.12 — 03.01.2027</h2><p>me/je: 20h30</p></div>'
        rows = parse_pulloff(soup(page), 'https://www.pulloff.ch/test/')
        self.assertEqual([(r['date'], r['time']) for r in rows], [('2026-12-30','20:30'),('2026-12-31','20:30')])

    def test_grange_music_and_truncation(self):
        card = '<a class="card" href="/test"><div class="event-card-title">Concert</div><div class="list-inline">Musique</div><div class="card-footer">16.10.2026</div></a>'
        detail = '<div class="event-right-content"><div class="border-bottom"><p>Ve 16.10, 20h30</p></div><div class="border-bottom"><p>&gt; La Grange</p></div></div>'
        with patch('expanded_adapters.config', MAX_DETAIL_PAGES=1):
            result = collect_grange(soup(card*2), 'https://grange-unil.ch/', Mock(return_value=detail))
        self.assertTrue(result.partial)
        self.assertEqual(result.events[0]['category'], 'Musique')
        self.assertEqual(result.events[0]['date'], '2026-10-16')

    def test_lagenda_reports_pagination_limit(self):
        form = soup('<form class="em-search-form"><select name="category[]"><option value="1">Musique</option></select></form>')
        listing = '<div class="em-pagination"><a title="suite">5</a><a title="suite">2</a><a title="suite">3</a><a title="suite">4</a></div>'
        with patch('expanded_adapters.parse_lagenda', return_value=[]), patch('expanded_adapters.config', MAX_AGENDA_PAGES=4, COLLECTION_HORIZON_DAYS=90):
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
        page = '<div class="action" data-idaction="1"><h4>Film 1971</h4><div class="projections"><a href="https://cityclub.ticketack.com/screening/buy/a">ve 31.12 / 20h30</a><a href="https://cityclub.ticketack.com/screening/buy/b">sa 1.1 / 18h</a></div></div>'
        a,b = parse_cityclub(soup(page), 'https://www.cityclubpully.ch/affiche/2026-12-00')
        self.assertEqual((a['date'],b['date']), ('2026-12-31','2027-01-01'))
        self.assertNotEqual(a['source_event_key'], b['source_event_key'])
        self.assertEqual(a['municipality'], 'Pully')

    def test_naftule_separates_performances_on_same_ticket_page(self):
        card = '<li data-show="test" data-genres="humour"><span>20H30</span><h3><a href="https://monbillet.ch/events/test">Spectacle</a></h3></li>'
        page = ''.join('<div data-day-panel data-day="'+day+'">'+card+'</div>' for day in ['2026-11-14','2026-11-15'])
        a,b = parse_naftule(soup(page), 'https://naftule.ch/programme/')
        self.assertNotEqual(a['date'],b['date'])
        self.assertNotIn('source_event_key', a)

    def test_boulimie_uses_only_explicit_weekday_schedule(self):
        page = '<h1 class="show-artist">Test</h1><div class="show-schedule">4 au 14 novembre 2026</div><div class="normal-text"><h6>Mercredi et jeudi: 19h<br>Vendredi: 20h<br>Samedi: 17h</h6></div>'
        rows = parse_boulimie(soup(page), 'https://theatreboulimie.com/spectacle/test/')
        self.assertEqual([r['date'] for r in rows], ['2026-11-04','2026-11-05','2026-11-06','2026-11-07','2026-11-11','2026-11-12','2026-11-13','2026-11-14'])
        self.assertEqual(rows[0]['time'], '19:00')
        [row] = parse_boulimie(soup(page.replace('<h6>','Ces soirées n\'ont pas lieu à Boulimie<h6>')), 'https://theatreboulimie.com/spectacle/test/')
        self.assertEqual(row['location'], '')

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
