import json
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

from agenda import TZ
from collection_quality import assess, venue_for
from expanded_adapters import collect_grange, parse_pulloff
from programme_adapters import parse_vidy, collect_programme, confirm_vidy, vidy_kind
from source_registry import active_sources


def soup(html):
    return BeautifulSoup(html, 'lxml')


def vidy_page(rows):
    data = {'props': {'pageProps': {'node': {'isCalendarPage': True, 'archive': {'eventDates': rows}}}}}
    return soup('<script id="__NEXT_DATA__" type="application/json">'+json.dumps(data)+'</script>')


def vidy_row(day='2026-11-01 19:30:00', room='Salle 17, Le Pavillon', state='ON_SALE'):
    return dict(date=day, location={'name':room}, state=state,
                event=dict(id=1, title='Spectacle &amp; test', link='/fr/evenement/test/',
                           startDate='2026-10-28 19:30:00', endDate='2026-11-30 21:00:00',
                           genres={'nodes':[{'translation':{'name':'Théâtre'}}]}))


def vidy_detail(sessions, genres=('Théâtre',)):
    blocks=[{'name':'supt/header-metas','attributes':{'genres':[{'title':g} for g in genres]}},
            {'name':'supt/section-dates-times','attributes':{'rows':sessions}}]
    data={'props':{'pageProps':{'node':{'blocksJSON':json.dumps(blocks)}}}}
    return '<script id="__NEXT_DATA__" type="application/json">'+json.dumps(data)+'</script>'


class ProgrammeTest(unittest.TestCase):
    def test_vidy_single_session_header_is_valid_but_a_date_range_is_not(self):
        for label,expected in [('Le 1 novembre 2026 <span>• 19:30</span>',True),('Du 1 au 3 novembre 2026',False)]:
            data={'props':{'pageProps':{'node':{'blocksJSON':json.dumps([{'name':'supt/header-metas','attributes':{
                'dates':label,'location':'Salle 17, Le Pavillon','genres':[{'title':'Théâtre'}]}}])}}}}
            html='<script id="__NEXT_DATA__" type="application/json">'+json.dumps(data)+'</script>'
            result=parse_vidy(vidy_page([vidy_row()]),'https://www.vidy.ch/fr/calendrier/')
            confirm_vidy(result,Mock(return_value=html),datetime(2026,10,17,tzinfo=TZ))
            self.assertEqual(result.events[0]['detail_confirmed'],expected)

    def test_vidy_confirms_each_session_and_keeps_disagreement_in_review(self):
        result=parse_vidy(vidy_page([vidy_row(),vidy_row('2026-11-02 20:00:00')]),'https://www.vidy.ch/fr/calendrier/')
        detail=vidy_detail([{'date':'2026-11-01 19:30:00','location':'Salle 17, Le Pavillon'},
                            {'date':'2026-11-02 20:30:00','location':'Salle 17, Le Pavillon'}])
        result=confirm_vidy(result,Mock(return_value=detail),datetime(2026,10,17,tzinfo=TZ))
        decisions=[assess(e,'https://www.vidy.ch/fr/calendrier/',datetime(2026,10,17,tzinfo=TZ)) for e in result.events]
        self.assertEqual([d['status'] for d in decisions],['candidate','review'])
        self.assertEqual(decisions[1]['reason'],'conflicting_published_dates')
        self.assertTrue(result.events[0]['evidence_url'].endswith('/fr/evenement/test/'))

    def test_vidy_daytime_session_requires_matching_official_detail(self):
        day = '2026-11-01 14:00:00'
        for confirmed_day, expected in [(day, 'candidate'), ('2026-11-01 14:30:00', 'review')]:
            result = parse_vidy(vidy_page([vidy_row(day)]), 'https://www.vidy.ch/fr/calendrier/')
            fetch = Mock(return_value=vidy_detail([{'date':confirmed_day, 'location':'Salle 17, Le Pavillon'}]))
            now = datetime(2026,10,17,tzinfo=TZ)
            confirm_vidy(result, fetch, now)
            fetch.assert_called_once()
            self.assertEqual(assess(result.events[0], 'https://www.vidy.ch/fr/calendrier/', now)['status'], expected)

    def test_vidy_failed_detail_cannot_publish_an_unconfirmed_calendar_row(self):
        from scraper import FetchError
        result=parse_vidy(vidy_page([vidy_row()]),'https://www.vidy.ch/fr/calendrier/')
        result=confirm_vidy(result,Mock(side_effect=FetchError('synthetic outage')),datetime(2026,10,17,tzinfo=TZ))
        self.assertFalse(result.events[0]['detail_confirmed'])
        self.assertIn('1 erreurs',result.method)

    def test_vidy_workshop_and_discussion_tags_do_not_become_performances(self):
        self.assertEqual(vidy_kind('Tuesday is Danceday',{'danse','workshop'})[0],'')
        self.assertEqual(vidy_kind('Rencontre avec les artistes',{'theatre'})[0],'')
        self.assertEqual(vidy_kind('Projection de Amleto',{'film','conference','theatre'})[0],'ScreeningEvent')

    def test_hango_rejects_recommended_events_from_a_different_known_venue(self):
        url='https://app.hango.ch/venues/chateau-music-club-zofhmvrmaepaiykgh08megmv'
        listing=soup('<a href="/events/one">One</a><a href="https://other.test/events/two">Two</a>')
        row={'@type':'Event','name':'Other venue','startDate':'2026-10-30T21:00:00Z',
             'keywords':'DJ set','location':{'@id':'https://app.hango.ch/venues/other','name':'Les Docks'}}
        fetch=Mock(return_value='<script type="application/ld+json">'+json.dumps(row)+'</script>')
        result=collect_programme(url,listing,fetch)
        self.assertEqual(result.events,[])
        fetch.assert_called_once_with('https://app.hango.ch/events/one')

    def test_hango_keeps_22h_local_before_and_after_clock_change(self):
        url='https://app.hango.ch/venues/chateau-music-club-zofhmvrmaepaiykgh08megmv'
        for start in ['2026-10-24T20:00:00Z','2026-10-30T21:00:00Z']:
            row={'@type':'Event','name':'DJ test','startDate':start,'keywords':'DJ set',
                 'location':{'@id':url,'name':'Château Music Club','address':{'addressLocality':'Lausanne'}}}
            result=collect_programme(url,soup('<a href="/events/one">One</a>'),Mock(return_value='<script type="application/ld+json">'+json.dumps(row)+'</script>'))
            self.assertEqual(result.events[0]['time'],'22:00')
            self.assertEqual(result.events[0]['event_kind'],'ClubNight')
    def test_pulloff_skips_exceptional_closures_and_separate_exhibition(self):
        page=soup('<div class="siteorigin-widget-tinymce"><h1>Test</h1><h2>30.10 — 19.11.2026</h2><p>(relâches exceptionnelles du 10.11 au 13.11)</p><p>LU : Relâche | MA/JE/SA : 19h | ME/VE : 20H | DI : 18H</p></div><div class="siteorigin-widget-tinymce"><h2>Exposition 12 — 21.11.2026</h2><p>ma: 10h30</p></div>')
        rows=parse_pulloff(page,'https://www.pulloff.ch/test/')
        self.assertEqual(len(rows),14)
        self.assertFalse(any('2026-11-10' <= e['date'] <= '2026-11-13' for e in rows))
        self.assertEqual(next(e['time'] for e in rows if e['date']=='2026-11-17'),'19:00')

    def test_pulloff_same_month_range_and_unknown_exception(self):
        page='<div class="siteorigin-widget-tinymce"><h1>Test</h1><h2>08 — 13.12.2026</h2><p>ma/je/sa: 19h | me/ve: 20h | di: 18h</p>{}</div>'
        self.assertEqual(len(parse_pulloff(soup(page.format('')),'https://www.pulloff.ch/test/')),6)
        rows=parse_pulloff(soup(page.format('<p>(relâches exceptionnelles à confirmer)</p>')),'https://www.pulloff.ch/test/')
        self.assertTrue(all(e['schedule_conflict'] for e in rows))

    def test_vidy_separates_sessions_without_using_show_end_range(self):
        result = parse_vidy(vidy_page([vidy_row(),vidy_row('2026-11-02 20:00:00')]), 'https://www.vidy.ch/fr/calendrier/')
        self.assertTrue(result.partial)
        a,b=result.events
        self.assertEqual(a['title'],'Spectacle & test')
        self.assertEqual(a['start_at'],'2026-11-01T19:30:00+01:00')
        self.assertNotIn('end_at',a)
        self.assertNotEqual(a['source_event_key'],b['source_event_key'])
        self.assertEqual(assess(a,'https://www.vidy.ch/fr/calendrier/',datetime(2026,10,17,tzinfo=TZ))['reason'],'missing_detail_confirmation')

    def test_vidy_offsite_midnight_and_cancellation_stay_out(self):
        result = parse_vidy(vidy_page([vidy_row(room='Comédie de Genève'),vidy_row('2026-11-01 00:00:00'),vidy_row(state='CANCELLED')]), 'https://www.vidy.ch/fr/calendrier/')
        decisions=[assess(e,'https://www.vidy.ch/fr/calendrier/',datetime(2026,10,17,tzinfo=TZ)) for e in result.events]
        self.assertEqual([d['reason'] for d in decisions],['unverified_or_out_of_scope_venue','unverified_start_time','cancelled'])

    def test_vidy_fails_on_missing_calendar_instead_of_reporting_empty(self):
        with self.assertRaises(ValueError):
            parse_vidy(soup('<h1>Maintenance</h1>'),'https://www.vidy.ch/')

    def test_satellite_excluded_even_from_an_aggregator(self):
        self.assertNotIn('SRC_L013',{s['id'] for s in active_sources()})
        event=dict(title='Test',location='Satellite')
        self.assertEqual(assess(event,'https://l-agenda.ch/')['reason'],'venue_out_of_scope')

    def test_chateau_and_pavillon_names_resolve_without_conflating_venues(self):
        self.assertEqual(venue_for('Brasserie du Château')['id'],venue_for('Château Music Club')['id'])
        self.assertNotEqual(venue_for('Le Pavillon')['id'],venue_for('Pavillon Naftule')['id'])

    def test_holy_monkey_does_not_borrow_footer_year_or_opening_hours(self):
        page=soup('<p class="wp-block-paragraph"><strong>JEUDI 12 NOVEMBRE<br>LOCAL METAL NIGHT</strong></p><footer>2026 JEUDI 17:30–00:00</footer>')
        [event]=collect_programme('https://holymonkey.ch/next-events/',page,Mock()).events
        self.assertEqual((event['date'],event['time']),('',''))
        self.assertNotIn('start_at',event)

    def test_grange_deduplicates_mobile_desktop_and_marks_unread_partial(self):
        card='<a class="card" href="/evenement/test/"><div class="event-card-title">Test</div><div class="list-inline">Théâtre</div><div class="card-footer">03.11.2026</div></a>'
        sidebar='<div class="event-right-content"><div class="border-bottom"><p>Ma 3.11, 19h</p></div><div class="border-bottom"><p>&gt; La Grange</p></div></div>'
        result=collect_grange(soup(card),'https://www.grange-unil.ch/',Mock(return_value=sidebar*2))
        self.assertEqual(len(result.events),1)
        self.assertEqual(result.events[0]['municipality'],'Ecublens')
        self.assertIn('vd.ch',result.events[0]['municipality_proof'])
        self.assertFalse(result.partial)
        result=collect_grange(soup(card),'https://www.grange-unil.ch/',Mock(return_value=sidebar.replace('Ma 3.11, 19h','Horaire à venir')))
        self.assertTrue(result.partial)
        self.assertEqual(result.events,[])

    def test_hungry_bear_keeps_date_without_inventing_a_session_time(self):
        page=soup('<h1 class="heading">Tournoi - 18/10/2026</h1><footer>Weekends 9am–6pm</footer>')
        [event]=collect_programme('https://www.hungrybearfood.ch/events',page,Mock()).events
        self.assertEqual(event['date'],'2026-10-18')
        self.assertEqual(event['time'],'')


if __name__=='__main__':
    unittest.main()
