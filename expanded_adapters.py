"""Additional official programmes, read without executing remote JavaScript.

Dates come from explicit programme fields, never publication timestamps.
Missing times remain missing and are kept out of the public programme.
"""
import re
from datetime import date
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from agenda import fold
from config import config
from collection_result import CollectionResult
from venue_adapters import clock, dotted_day, set_start, text


# Compatibility import during the incremental package migration. The dispatch
# below and older callers use this name; the implementation now lives in the
# named adapter module.
from samstag.collection.adapters.boulimie import parse_boulimie
from samstag.collection.adapters.cityclub import parse_cityclub
from samstag.collection.adapters.common import event_at, french_day
from samstag.collection.adapters.naftule import parse_naftule
from samstag.collection.adapters.arsenic import parse_arsenic
from samstag.collection.adapters.grange import collect_grange
from samstag.collection.adapters.pulloff import parse_pulloff
from samstag.collection.adapters.folklor import parse_folklor
from samstag.collection.adapters.mad import parse_mad_ticket
from samstag.collection.adapters.jazzonze import collect_jazzonze, parse_jazzonze
from samstag.collection.adapters.lagenda import collect_lagenda, parse_lagenda


def parse_breche(soup, url):
    title = " + ".join(n.get_text(" ", strip=True) for n in soup.select(".artist-div-2 .h2-2") if n.get_text(strip=True))
    if not title:
        return []
    event = event_at(title, url, url, "La Brèche", "", "Culture")
    event["source_event_key"] = url
    title_text = soup.title.get_text(" ", strip=True) if soup.title else ""
    day = dotted_day(title_text)
    content = soup.get_text(" ", strip=True)
    opening = re.search(r"Portes\s*:\s*(\d{1,2}h\d{0,2})", content, re.I)
    start = re.search(r"Début\s*:\s*(\d{1,2}h\d{0,2})", content, re.I)
    if opening and clock(opening[1]):
        event["doors_time"] = clock(opening[1]).strftime("%H:%M")
    set_start(event, day, clock(start[1]) if start else None)
    # An explicit ticket URL supplies the event family; don't classify
    # every item in a multidisciplinary programme as a concert.
    if soup.select_one('a[href*="petzi.ch"]') and "a people's history" not in fold(title):
        event.update(event_kind="MusicEvent", category="Musique")
    if "halloween" in fold(title):
        event.update(event_kind="ClubNight", category="Clubbing")
    if "impro" in fold(title):
        event.update(event_kind="TheaterEvent", category="Théâtre")
    paragraphs = [n.get_text(' ', strip=True).replace('\u200d', '').strip()
                  for n in soup.select('.div-flexbox-artiste .hyphen.w-richtext p')]
    event["description"] = '\n\n'.join(p for p in paragraphs if p) or text(soup, ".rich-text-block")[:400]
    return [event]


def parse_oblo(soup, url):
    events = []
    for card in soup.select('a[href^="/events/"]'):
        target = urljoin(url, card["href"])
        match = re.fullmatch(r"/events/(\d{4}-\d{2}-\d{2})-(\d{2})-(\d{2})/?", urlparse(target).path)
        spans = [n.get_text(" ", strip=True) for n in card.select("span")]
        if not match or len(spans) != 5:
            continue
        title, genres = spans[3], fold(spans[4])
        kind = "ScreeningEvent" if any(w in genres for w in ["metrage", "documentaire", "cinema"]) else "TheaterEvent" if "performances" in genres else ""
        event = event_at(title, target, url, "Cinéma Oblò", kind, "Cinéma" if kind == "ScreeningEvent" else "Théâtre" if kind else "Culture")
        day = date.fromisoformat(match[1])
        hour = clock(match[2]+":"+match[3])
        visible = clock(spans[2])
        # Cross-check encoded time with the actual programme label.
        if hour == visible and str(day.day) == re.sub(r"^0", "", spans[1].split()[0]):
            set_start(event, day, hour)
        event.update(description=spans[4], source_event_key=target)
        events.append(event)
    if not events:
        raise ValueError("Programme Oblò absent ou structure modifiée")
    return events


def collect_expanded(url, soup, fetch):
    host = (urlparse(url).hostname or "").removeprefix("www.")
    if host == "folklor.club":
        return parse_folklor(soup, url), "folklor-programme-v3"
    if host == "naftule.ch":
        return parse_naftule(soup, url), "naftule-performances-v3"
    if host == "oblo.ch":
        return parse_oblo(soup, url), "oblo-programme-v3"
    if host == "jazzonzeplus.ch":
        return collect_jazzonze(soup, url, fetch)
    if host == "arsenic.ch":
        return parse_arsenic(soup, url), "arsenic-public-calendar-v3"
    if host == "l-agenda.ch":
        return collect_lagenda(soup, url, fetch)
    if host == "grange-unil.ch":
        return collect_grange(soup,url,fetch)
    if host == "cityclubpully.ch":
        # Follow the current month actually advertised by the official site.
        month_links = list(dict.fromkeys(urljoin(url, a["href"]) for a in soup.select('a[href]')
                          if re.fullmatch(r"/affiche/\d{4}-\d{2}-00/?", urlparse(a["href"]).path)))
        if not month_links:
            raise ValueError("Lien vers le programme mensuel CityClub absent")
        events = []
        for target in month_links[:2]:
            events.extend(parse_cityclub(BeautifulSoup(fetch(target), "lxml"), target))
        return events, "cityclub-monthly-sessions-v3"
    if host in {"la-breche.fun", "theatreboulimie.com", "mad.club", "pulloff.ch"}:
        if host == "mad.club" and urlparse(url).path.rstrip("/") != "/agenda":
            link = soup.select_one('a[href="https://www.mad.club/agenda/"]')
            if not link:
                raise ValueError("Lien agenda MAD absent")
            soup = BeautifulSoup(fetch(link["href"]), "lxml")
        parsers = {"la-breche.fun": parse_breche, "theatreboulimie.com": parse_boulimie, "mad.club": parse_mad_ticket, "pulloff.ch":parse_pulloff}
        targets, agenda_dates = [], {}
        for a in soup.select("a[href]"):
            target = urljoin(url, a["href"])
            parsed = urlparse(target)
            match = ((host == "la-breche.fun" and parsed.hostname in {"www.la-breche.fun", "la-breche.fun"} and parsed.path.startswith("/events/"))
                     or (host == "theatreboulimie.com" and parsed.hostname == "theatreboulimie.com" and parsed.path.startswith("/spectacle/"))
                     or (host == "mad.club" and parsed.hostname == "www.mad-shop.ch" and "product=ticket-" in parsed.query)
                     or (host == 'pulloff.ch' and parsed.hostname == 'www.pulloff.ch' and fold(a.get_text(' ',strip=True)) == 'en savoir plus'))
            if match and target not in targets:
                targets.append(target)
                if host == 'mad.club':
                    for parent in a.parents:
                        if parent.name == 'body':
                            break
                        headings = parent.select('h3')
                        if len(headings) >= 2:
                            day = french_day(headings[0].get_text(' ',strip=True))
                            if day:
                                agenda_dates[target] = day.isoformat()
                                break
        if not targets:
            raise ValueError("Liens de fiches événement absents du programme")
        events, failures = [], 0
        for target in targets[:config.MAX_DETAIL_PAGES]:
            try:
                rows = parsers[host](BeautifulSoup(fetch(target), "lxml"), target)
                for event in rows:
                    if target in agenda_dates:
                        event['agenda_date'] = agenda_dates[target]
                        if event.get('date') != agenda_dates[target]:
                            event['schedule_conflict'] = True
                events.extend(rows)
            except Exception as exc:
                # Keep other details, but never claim a complete snapshot.
                import logging
                logging.getLogger(__name__).warning("Detail failed %s: %s", target, exc)
                failures += 1
        checked = min(len(targets), config.MAX_DETAIL_PAGES)
        read = checked - failures
        parse_status = "error" if failures == checked else "partial" if failures else "ok"
        completeness = "limited" if len(targets) > checked else "partial" if failures else "complete"
        return CollectionResult(
            events,
            f"{host}-v3: {len(targets)} liens, {checked} contrôlés, {failures} erreurs",
            complete_snapshot=not failures and len(targets) <= checked,
            partial=bool(failures or len(targets) > checked),
            pages_expected=len(targets), pages_read=read,
            parse_status=parse_status, completeness_status=completeness,
        )
    return None
