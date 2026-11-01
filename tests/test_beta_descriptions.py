import unittest
from bs4 import BeautifulSoup
from expanded_adapters import parse_pulloff,parse_breche

class DescriptionTest(unittest.TestCase):
    def test_pulloff_does_not_mix_neighbour_exhibition(self):
        soup=BeautifulSoup('''<div class="siteorigin-widget-tinymce"><h1>Spectacle de test</h1><h2>30.10 — 19.11.2026</h2><p>Présentation du spectacle.</p></div>
        <div class="siteorigin-widget-tinymce"><h1>Exposition voisine</h1><p>Adresse et texte de la galerie.</p></div>''','lxml')
        rows=parse_pulloff(soup,'https://www.pulloff.ch/test/')
        self.assertTrue(rows)
        self.assertTrue(all(e['description']=='Présentation du spectacle.' for e in rows))

    def test_breche_collects_artist_prose_not_navigation(self):
        soup=BeautifulSoup('''<div class="artist-div-2"><h2 class="h2-2">Artiste de test</h2></div>
        <div class="div-flexbox-artiste"><div class="hyphen w-richtext"><p>Un premier texte officiel.</p><p>Un second paragraphe.</p></div></div>
        <footer><p>Texte sans lien avec le concert.</p></footer>''','lxml')
        event=parse_breche(soup,'https://www.la-breche.fun/events/test')[0]
        self.assertEqual(event['description'],'Un premier texte officiel.\n\nUn second paragraphe.')
