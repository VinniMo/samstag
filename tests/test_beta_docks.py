"""Regressions from the official Cat Power page inspected for the beta."""
import unittest
from bs4 import BeautifulSoup
from venue_adapters import parse_docks

class DocksBetaTest(unittest.TestCase):
    def page(self, alert='', prose=''):
        return BeautifulSoup(f'''<h1>Concert</h1><div class="event-infos-and-ticketing">
        <div><span class="event-info-date">23.10.2026</span></div>
        <div class="event-ticketing">{alert}</div></div>
        <div class="event-container"><div class="artist-content"><div class="the-content">{prose}</div></div></div>
        <aside>Complet Annulé <p>Recommandations</p></aside>''', 'html.parser')

    def test_ticketing_status_outside_date_parent_is_read(self):
        row = parse_docks(self.page('<span>Complet</span>'), 'https://www.docks.ch/event')
        self.assertEqual(row['availability'], 'sold_out')
        cancelled = parse_docks(self.page('<span>Annulé</span>'), 'https://www.docks.ch/event')
        self.assertEqual(cancelled['event_status'], 'EventCancelled')

    def test_recommendations_do_not_change_status(self):
        row = parse_docks(self.page(), 'https://www.docks.ch/event')
        self.assertNotIn('availability', row)
        self.assertNotIn('event_status', row)

    def test_artist_prose_is_preserved_beyond_four_hundred_characters(self):
        prose = 'Une description officielle. ' * 25
        row = parse_docks(self.page(prose=f'<p>{prose}</p><p>Dernier paragraphe.</p>'), 'https://www.docks.ch/event')
        self.assertEqual(row['description'], prose.strip()+'\n\nDernier paragraphe.')
