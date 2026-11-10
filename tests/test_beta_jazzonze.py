import unittest
from datetime import datetime,timedelta
from bs4 import BeautifulSoup
from expanded_adapters import parse_jazzonze,collect_jazzonze
from samstag.collection.adapters.jazzonze import parse_jazzonze as packaged_parse_jazzonze, collect_jazzonze as packaged_collect_jazzonze
from venue_adapters import MONTHS,TZ

class JazzOnzeBetaTest(unittest.TestCase):
    def test_legacy_imports_are_packaged_adapters(self):
        self.assertIs(parse_jazzonze, packaged_parse_jazzonze)
        self.assertIs(collect_jazzonze, packaged_collect_jazzonze)

    def listing(self):
        day=datetime.now(TZ).date()+timedelta(days=1)
        label=f'{day.day} {list(MONTHS)[day.month-1]} {day.year}'
        return BeautifulSoup(f'''<p><a href="https://www.google.ch/maps?q=casino">Casino de Montbenon (Salle Paderewski et Salle des Fêtes)</a><br>Allée Ernest-Ansermet 3<br>1003 Lausanne</p>
        <p>Administration : Rue de Genève 21, 1003 Lausanne</p>
        <div class="rfp-item"><h2 class="rfp-item-title">Concert de test</h2>
        <div class="program">{label} / Salle Paderewski / 20h / CHF 55.-</div>
        <a class="rfp-mask" href="/concert/"></a></div>''','lxml')

    def test_venue_access_address_never_administration(self):
        event=parse_jazzonze(self.listing(),'https://jazzonzeplus.ch/')[0]
        self.assertEqual(event['address'],'Allée Ernest-Ansermet 3 1003 Lausanne')
        self.assertEqual(event['address_proof'],'https://jazzonzeplus.ch/')

    def test_missing_access_address_is_not_invented(self):
        listing=self.listing();listing.p.decompose()
        self.assertFalse(parse_jazzonze(listing,'https://jazzonzeplus.ch/')[0].get('address'))

    def test_daytime_concert_gets_official_description(self):
        listing = self.listing()
        node = listing.select_one('.program')
        node.string = node.get_text().replace('20h', '14h')
        result = collect_jazzonze(listing, 'https://jazzonzeplus.ch/', lambda _: '<h1 class="entry-title">Concert de test</h1><article><div class="entry-content"><p>Concert en journée.</p></div></article>')
        self.assertEqual(result.events[0]['time'], '14:00')
        self.assertEqual(result.events[0]['description'], 'Concert en journée.')

    def test_description_requires_matching_artist(self):
        def detail(title):return f'<h1 class="entry-title">{title}</h1><article><div class="entry-content"><p>Biographie officielle du concert.</p></div></article>'
        good=collect_jazzonze(self.listing(),'https://jazzonzeplus.ch/',lambda _:detail('Concert de test'))
        self.assertEqual(good.events[0]['description'],'Biographie officielle du concert.')
        wrong=collect_jazzonze(self.listing(),'https://jazzonzeplus.ch/',lambda _:detail('Autre concert'))
        self.assertTrue(wrong.partial)
        self.assertFalse(wrong.events[0].get('description'))
