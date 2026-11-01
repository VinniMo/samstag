"""Regressions: covered venues cannot fall back to tourism, even after approval."""
import unittest
from datetime import datetime
from bs4 import BeautifulSoup
import collection_quality as quality
import venue_adapters
from tests import test_collection_pipeline as pipeline


class OfficialSourcePolicyTest(unittest.TestCase):
    setUp = pipeline.PipelineTest.setUp
    tearDown = pipeline.PipelineTest.tearDown
    def test_covered_venue_tourism_is_blocked_without_exact_title_match(self):
        source = 'https://www.lausanne-tourisme.ch/fr/evenement/'
        raw = {**self.raw, 'location': 'D! Club', 'title': 'Different imported title',
               'url': source+'test/', 'evidence_url': source+'test/'}
        item = quality.assess(raw, source)
        self.assertEqual(item['reason'], 'official_source_required_for_covered_venue')
        db = __import__('db')
        db.stage_collection(item)
        self.assertEqual(db.list_public_events(), [])
        # Existing approvals are revalidated too: no migration window leaks links.
        item['status'] = 'approved'
        self.assertFalse(quality.publicly_visible(item))

    def test_tourism_destination_cannot_be_disguised_as_official_source(self):
        item = quality.assess({**self.raw, 'location': 'D! Club',
                              'url':'https://www.lausanne-tourisme.ch/fr/evenement/test/'},
                             'https://dclub.ch/agenda/')
        self.assertEqual(item['status'], 'review')


class DclubConcertTest(unittest.TestCase):
    def test_officially_linked_registration_supplies_artistic_time_only_when_matching(self):
        today = datetime.now(venue_adapters.TZ).date()
        url = 'https://dclub.ch/agenda/'
        detail_url = url+today.strftime('%Y%m%d')+'/test#d-club-live'
        ticket = 'https://visaevents.swoogo.com/test'
        agenda = BeautifulSoup(f'''<div class="event" data-date="{today:%Y%m%d}" data-place='["d-club"]' data-styles='["concert"]'>
        <a class="main" href="{detail_url}"><header class="dtitle">Concert synthétique</header><div class="header"><span class="name">Artiste test</span></div></a>
        <p class="door">Porte: 20:00</p></div>''','lxml')
        detail = f'''<div id="d-club-live"><h2 class="date-title">Concert synthétique</h2>
        <div class="dclub-date-content"><div>Concert gratuit sur inscription.</div></div>
        <div class="action"><a href="{ticket}">prélocation</a></div></div>'''
        registration = f'D! Club {today.day} {list(venue_adapters.MONTHS)[today.month-1]} Artiste test Concert: 20h30'
        def collect(body):
            pages = {detail_url.split('#')[0]:detail, ticket:body}
            return venue_adapters.collect_dclub(agenda,url,pages.__getitem__).events[0]
        row = collect(registration)
        self.assertEqual(row['title'], 'Concert synthétique')
        self.assertEqual(row['time'], '20:30')
        self.assertEqual(row['doors_time'], '20:00')
        self.assertEqual(row['price'], 'Gratuit sur inscription')
        self.assertEqual(row['url'],detail_url)
        self.assertNotIn('access_conditions', row)
        lottery = collect(registration + ' Les gagnants sont tirés au sort parmi les inscrits.')
        self.assertIn('tirage au sort', lottery['access_conditions'])
        now = datetime.combine(today, datetime.min.time(), venue_adapters.TZ)
        self.assertEqual(quality.assess(row,url,now)['status'],'candidate')
        for body in [registration.replace('Artiste test','Autre artiste'),
                     registration.replace('D! Club','Autre salle'),
                     registration+' Concert: 21h00', registration.replace('Concert: 20h30','')]:
            with self.subTest(body=body):
                rejected = collect(body)
                self.assertEqual(rejected['time_role'],'doors')
                self.assertEqual(quality.assess(rejected,url,now)['reason'],'doors_not_artistic_start')
        result = venue_adapters.collect_dclub(agenda,url,lambda _: (_ for _ in ()).throw(RuntimeError('offline')))
        self.assertTrue(result.partial)
        self.assertEqual(result.events[0]['time_role'],'doors')
