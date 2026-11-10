"""Additional official programmes, read without executing remote JavaScript.

Dates come from explicit programme fields, never publication timestamps.
Missing times remain missing and are kept out of the public programme.
"""
import json
from html import unescape
import re
from datetime import date, datetime, timedelta
from urllib.parse import urljoin, urlparse, urlencode

from bs4 import BeautifulSoup

from agenda import TZ, fold
from config import config
from collection_result import CollectionResult
from venue_adapters import MONTHS, clock, dotted_day, set_start, text


# Compatibility import during the incremental package migration. The dispatch
# below and older callers use this name; the implementation now lives in the
# named adapter module.
from samstag.collection.adapters.boulimie import parse_boulimie
from samstag.collection.adapters.cityclub import parse_cityclub
from samstag.collection.adapters.common import event_at, french_day
from samstag.collection.adapters.naftule import parse_naftule


def parse_folklor(soup, url):
    cards = soup.select("#program article.event")
    if not cards:
        raise ValueError("Programme Folklor absent ou structure modifiée")
    events = []
    for card in cards:
        title = text(card, ".event-title")
        if not title:
            continue
        link = card.select_one(".event-artists a[href]")
        target = urljoin(url, link["href"]) if link else url
        event = event_at(title, target, url, "Folklor", "ClubNight", "Clubbing")
        set_start(event, dotted_day(text(card, ".event-date")), clock(text(card, ".event-time")))
        event["description"] = text(card, ".event-artists")[:400]
        if link:
            event["source_event_key"] = target
        events.append(event)
    return events


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


def parse_arsenic(soup, url):
    marker = re.search(r"\bvar\s+spectacles\s*=\s*", str(soup))
    if not marker:
        raise ValueError("Données publiques du calendrier Arsenic absentes")
    rows, _ = json.JSONDecoder().raw_decode(str(soup)[marker.end():])
    if not isinstance(rows, list):
        raise ValueError("Format de calendrier Arsenic modifié")
    events = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        genre = fold(unescape(row.get("description", "")))
        author = unescape(row.get("auteur", ""))
        kind, category = "", "Culture"
        if "dj" in fold(author) or "dj sets" in genre:
            kind, category = "ClubNight", "Clubbing"
        elif "danse" in genre:
            kind, category = "DanceEvent", "Danse"
        elif any(w in genre for w in ["theatre", "performance"]):
            kind, category = "TheaterEvent", "Théâtre"
        for value in row.get("dates", []):
            event = event_at(" — ".join(filter(None, [author, unescape(row.get("title", ""))])),
                             row.get("link", url), url, "Arsenic", kind, category)
            try:
                start = datetime.strptime(value, "%Y-%m-%d %H:%M")
                # Source's nohour flags explicitly invalidate placeholder times.
                if value not in row.get("nohour", []) and value.split()[0] not in row.get("nohour", []):
                    set_start(event, start.date(), start.time())
            except (ValueError, TypeError):
                pass
            event["description"] = unescape(row.get("description", ""))
            event["image"] = row.get("img", {}).get("src", "") if isinstance(row.get("img"), dict) else ""
            event["price"] = "Gratuit" if str(row.get("gratuit", "")) == "1" else ""
            if row.get("canceled"):
                event["event_status"] = "EventCancelled"
            # A spectacle page is a series, never one stable occurrence key.
            events.append(event)
    return events


def parse_lagenda(soup, url):
    from collection_quality import venue_for
    events = []
    for card in soup.select(".em-item-info"):
        link = card.select_one(".em-item-title a[href]")
        if not link:
            continue
        target = urljoin(url, link["href"])
        name = text(card, ".em-event-location a")
        event = event_at(link.get_text(" ", strip=True), target, url, name, "", "Culture")
        event["municipality"] = ""
        venue = venue_for(name)
        if venue and venue.get("adresse_statut") == "Confirmée":
            event.update(municipality=venue["commune"], address=venue["adresse"],
                         address_proof=venue["preuve"], venue_basis="exact_named_location_in_verified_registry")
        tags = fold(text(card, ".event-categories"))
        if any(w in tags for w in ["humour", "stand-up", "comedie"]):
            event.update(event_kind="ComedyEvent", category="Humour")
        elif "danse" in tags:
            event.update(event_kind="DanceEvent", category="Danse")
        elif any(w in tags for w in ["musique", "jazz", "rock", "electro", "classique", "pop", "opera"]):
            event.update(event_kind="MusicEvent", category="Musique")
        elif "theatre" in tags or "performance" in tags:
            event.update(event_kind="TheaterEvent", category="Théâtre")
        elif "projection" in tags or "film" in tags:
            event.update(event_kind="ScreeningEvent", category="Cinéma")
        dates = text(card, ".em-event-date")
        day = dotted_day(dates) if len(re.findall(r"\d{1,2}/\d{1,2}/\d{4}", dates)) == 1 else None
        set_start(event, day, clock(text(card, ".em-event-time")))
        event["description"] = text(card, ".em-item-desc")[:400]
        events.append(event)
    return events


def collect_lagenda(soup, url, fetch):
    form = soup.select_one("form.em-search-form")
    if not form:
        raise ValueError("Formulaire public L’Agenda absent ou modifié")
    # Use current published taxonomy identifiers, rather than hard-coded IDs.
    categories = []
    for option in form.select('select[name="category[]"] option[value]'):
        label = fold(option.get_text(" ", strip=True))
        if any(w in label for w in ["musique", "jazz", "rock", "pop", "electro", "humour", "stand-up", "danse", "theatre", "projection", "comedie", "classique", "opera", "performance"]):
            categories.append(option["value"])
    if not categories:
        raise ValueError("Catégories pertinentes absentes du formulaire L’Agenda")
    today = datetime.now(TZ).date()
    events, checks = [], 0
    truncated = False
    # Broad regional feeds include the immediate neighbouring municipalities.
    for region in ["Lausanne", "Ouest lausannois"]:
        params = [("action", "search_events"), ("view_id", "1"), ("region", region),
                  ("scope[0]", today.isoformat()),
                  ("scope[1]", (today+timedelta(days=config.COLLECTION_HORIZON_DAYS)).isoformat())]
        params += [("category[]", c) for c in categories]
        target = url.split("?", 1)[0] + "?" + urlencode(params)
        for page_number in range(1, config.MAX_AGENDA_PAGES + 1):
            page_url = target + "&pno="+str(page_number)
            listing = BeautifulSoup(fetch(page_url), "lxml")
            rows = parse_lagenda(listing, page_url)
            events.extend(rows); checks += 1
            pages = [a.get_text(strip=True) for a in listing.select('.em-pagination a[title]')]
            if str(page_number+1) not in pages:
                break
            if page_number == config.MAX_AGENDA_PAGES:
                truncated = True
    return CollectionResult(events, f"lagenda-filtered-v3: {checks} pages contrôlées, maximum {config.MAX_AGENDA_PAGES} par région (sélection filtrée)", partial=truncated)


def parse_jazzonze(soup, url):
    events = []
    labels = {
        'Casino de Montbenon (Salle Paderewski et Salle des Fêtes)': ['Salle Paderewski', 'Salle des Fêtes'],
        'Jumeaux Jazz Club': ['Jumeaux Jazz Club'],
        'BCV Concert Hall': ['BCV Concert Hall'],
        'EJMA (Atrium et Auditorium)': ['Atrium de l’EJMA', 'Auditorium de l’EJMA'],
    }
    addresses = {}
    for anchor in soup.select('a[href]'):
        label = anchor.get_text(' ', strip=True)
        if label not in labels or 'google.' not in anchor['href']:
            continue
        # Keep the named access block, never the festival administration address.
        for parent in list(anchor.parents)[:3]:
            value = parent.get_text(' ', strip=True).removeprefix(label).strip()
            if re.fullmatch(r'[^\d]+\d+[^\d]*\s+1003\s+Lausanne', value):
                for venue in labels[label]: addresses[venue] = value
                break
    for card in soup.select(".rfp-item"):
        title = text(card, ".rfp-item-title")
        parts = [s.strip() for s in text(card, ".program").split("/")]
        link = card.select_one("a.rfp-mask[href]")
        if not title or len(parts) != 4 or not link:
            continue
        venue = parts[1].replace("'", "’")
        event = event_at(title, urljoin(url, link["href"]), url, venue, "MusicEvent", "Musique")
        if venue in addresses:
            event.update(address=addresses[venue], address_proof=url)
        set_start(event, french_day(parts[0]), clock(parts[2]))
        event["price"] = parts[3]
        event["source_event_key"] = event["url"]
        if "annule" in fold(title):
            event["event_status"] = "EventCancelled"
        # Midnight is printed beneath the preceding evening date in this
        # programme; keep it for review until the ticket confirms civil date.
        if event.get("time") == "00:00":
            event["time_role"] = "unverified"
        image = card.select_one("img[src]")
        event["image"] = image["src"] if image else ""
        events.append(event)
    if not events:
        raise ValueError("Programme JazzOnze+ absent ou structure modifiée")
    return events


def collect_jazzonze(soup, url, fetch):
    events = parse_jazzonze(soup, url)
    today = datetime.now(TZ).date()
    checked, partial = 0, False
    for event in events:
        if not event.get('date') or not today <= date.fromisoformat(event['date']) <= today + timedelta(days=config.COLLECTION_HORIZON_DAYS):
            continue
        if event.get('event_status') == 'EventCancelled' or not event.get('time'):
            continue
        if checked >= config.MAX_DETAIL_PAGES or urlparse(event['url']).hostname != urlparse(url).hostname:
            partial = True
            continue
        checked += 1
        try:
            detail = BeautifulSoup(fetch(event['url']), 'lxml')
            if fold(text(detail, 'h1.entry-title')) != fold(event['title']):
                partial = True
                continue
            paragraphs = [n.get_text(' ', strip=True) for n in detail.select('article .entry-content > p')]
            event['description'] = '\n\n'.join(p for p in paragraphs if p)
            event['description_evidence_url'] = event['url']
        except Exception:
            partial = True
    return CollectionResult(events, f'jazzonze-programme-v3: {checked} fiches contrôlées', partial=partial)


def parse_pulloff(soup, url):
    heading = soup.select_one('.siteorigin-widget-tinymce h1')
    if not heading:
        raise ValueError("Titre de spectacle Pulloff absent")
    title = heading.get_text(' ', strip=True)
    # A second widget may advertise an off-site exhibition with its own dates.
    programme = heading.find_parent(class_='siteorigin-widget-tinymce')
    # Only this show's widget; a neighbouring widget can advertise an exhibition.
    description = '\n\n'.join(p.get_text(' ', strip=True) for p in programme.find_all('p', recursive=False)
                                if p.get_text(strip=True))
    dates = None
    for heading in programme.select('h2'):
        match = re.fullmatch(r"(\d{2})(?:\.(\d{2}))?\s*[—–-]\s*(\d{2})\.(\d{2})\.(\d{4})", heading.get_text(' ',strip=True))
        if match:
            year = int(match[5])
            first_month = int(match[2] or match[4])
            try:
                begin = date(year-int(first_month > int(match[4])), first_month, int(match[1]))
                end = date(year, int(match[4]), int(match[3]))
                if timedelta(0) <= end-begin <= timedelta(days=90):
                    dates = [begin+timedelta(days=n) for n in range((end-begin).days+1)]
            except ValueError:
                pass
            break
    content = programme.get_text(' ',strip=True)
    exceptions = re.findall(r'relaches? exceptionnelles?[^)]*', fold(content))
    uncertain_exception = False
    for exception in exceptions:
        match = re.fullmatch(r'relaches? exceptionnelles? du (\d{1,2})\.(\d{1,2}) au (\d{1,2})\.(\d{1,2})\s*', exception)
        if not match or not dates:
            uncertain_exception = True
            continue
        ranges = []
        for year in {d.year for d in dates}:
            try:
                a = date(year, int(match[2]), int(match[1]))
                b = date(year + int(int(match[4]) < int(match[2])), int(match[4]), int(match[3]))
                if a <= b and dates[0] <= a <= b <= dates[-1]:
                    ranges.append((a,b))
            except ValueError:
                pass
        if len(ranges) == 1:
            a,b = ranges[0]
            dates = [d for d in dates if not a <= d <= b]
        else:
            uncertain_exception = True
    hours = {}
    weekdays = ['lu','ma','me','je','ve','sa','di']
    for match in re.finditer(r"\b((?:lu|ma|me|je|ve|sa|di)(?:/(?:lu|ma|me|je|ve|sa|di))*)\s*:\s*(\d{1,2}[hH:]\d{0,2})\b", fold(content)):
        hour = clock(match[2])
        if hour:
            for value in match[1].split('/'):
                hours[weekdays.index(value)] = hour
    events = []
    for day in dates or []:
        if day.weekday() not in hours:
            continue
        event = event_at(title, url, url, 'Pulloff Théâtres', 'TheaterEvent', 'Théâtre')
        set_start(event, day, hours[day.weekday()])
        if uncertain_exception:
            event['schedule_conflict'] = True
        events.append(event)
    if not events:
        events = [event_at(title, url, url, 'Pulloff Théâtres', 'TheaterEvent', 'Théâtre')]
    for event in events:
        event['description'] = description
    return events


def collect_grange(soup, url, fetch):
    events = []
    programme = soup.select_one('a[href*="/recherche-dactivites/"]')
    if programme and urlparse(url).path.rstrip('/') != '/recherche-dactivites':
        target = urljoin(url, programme['href'])
        if (urlparse(target).hostname or '').removeprefix('www.') == 'grange-unil.ch':
            soup = BeautifulSoup(fetch(target), 'lxml')
    cards = soup.select('a.card[href]')
    checked, failed, unread = 0, 0, 0
    targets = set()
    for card in cards[:config.MAX_DETAIL_PAGES]:
        title = text(card, '.event-card-title')
        genres = fold(text(card, '.list-inline'))
        if not title or not any(w in genres for w in ['danse','theatre','performance','musique']):
            continue
        kind, category = (('DanceEvent','Danse') if 'danse' in genres else
                          ('MusicEvent','Musique') if 'musique' in genres else ('TheaterEvent','Théâtre'))
        # Workshops remain outside the admitted event types.
        if 'atelier' in genres:
            continue
        days = [dotted_day(value) for value in re.findall(r'\d{1,2}\.\d{1,2}\.\d{4}', text(card,'.card-footer'))]
        if not days or any(d is None for d in days):
            continue
        target = urljoin(url, card['href'])
        if (urlparse(target).hostname or '').removeprefix('www.') != 'grange-unil.ch':
            continue
        if target in targets:
            continue
        targets.add(target)
        checked += 1
        try:
            detail = BeautifulSoup(fetch(target),'lxml')
            panels = detail.select('.event-right-content')
            seen = set()
            before = len(events)
            for panel in panels:
                # Venue and session times are sibling blocks within the same
                # sidebar. Never borrow a location from the page footer.
                if not any(re.fullmatch(r'>\s*La\s+Grange', p.get_text(' ', strip=True)) for p in panel.select('p')):
                    continue
                for line in panel.select('p'):
                    match = re.match(r'^(Lu|Ma|Me|Je|Ve|Sa|Di)\s+(\d{1,2})\.(\d{1,2}),\s*(\d{1,2}h\d{0,2})\b',line.get_text(' ',strip=True))
                    if not match:
                        continue
                    possibilities = []
                    for year in range(min(days).year, max(days).year+1):
                        try:
                            day = date(year,int(match[3]),int(match[2]))
                            if min(days) <= day <= max(days):
                                possibilities.append(day)
                        except ValueError:
                            continue
                    if len(possibilities) != 1:
                        continue
                    day = possibilities[0]
                    key = (day,match[4])
                    if key in seen:
                        continue
                    seen.add(key)
                    event = event_at(title,target,target,'La Grange UNIL',kind,category)
                    from source_registry import VENUES
                    venue = next(v for v in VENUES if v['id'] == 'L029')
                    event['municipality'] = venue['commune']
                    event['municipality_proof'] = venue.get('preuve_commune', '')
                    set_start(event,day,clock(match[4]))
                    events.append(event)
            if len(events) == before:
                unread += 1
        except Exception:
            failed += 1
    if not checked:
        raise ValueError('Aucune fiche de spectacle datée trouvée à La Grange')
    return CollectionResult(events,f'grange-programme-v3: {checked} fiches, {failed} erreurs, {unread} sans séance lisible',partial=bool(failed or unread or len(cards) > config.MAX_DETAIL_PAGES))


def parse_mad_ticket(soup, url):
    product = soup.select_one(".product")
    if not product:
        raise ValueError("Fiche de billetterie MAD absente")
    content = product.get_text(" ", strip=True)
    # Limit parsing to the product, never related-event cards or page footer.
    title = text(product, ".product_title")
    event = event_at(title, url, url, "MAD Club", "ClubNight", "Clubbing")
    event.update(source_event_key=url, time_role="doors")
    month_names = {**MONTHS, **{k[:3]: v for k, v in MONTHS.items()}}
    date_label = text(product, ".summary > h3") or title
    found = re.search(r"\b(\d{1,2})\s+(\w+)\s+(\d{4})\b", fold(date_label))
    day = None
    if found and found[2] in month_names:
        day = date(int(found[3]), month_names[found[2]], int(found[1]))
    start = re.search(r"ouverture des portes\s*:?\s*(\d{1,2}h\d{0,2})", fold(content))
    set_start(event, day, clock(start[1]) if start else None)
    # A MAD shop also sells Montreux, boat and other off-site events.
    summary_title = product.select_one('.summary > h1')
    details = summary_title.find_next_sibling('div') if summary_title else None
    venue_label = details.get_text(" ", strip=True) if details else content
    if not re.search(r"\b(?:mad\s+(?:mainfloor|jetlag|club)|jetlag)\b", fold(venue_label)) or "montreux" in fold(title):
        event.update(location="", municipality="")
    for room in ["Mainfloor", "JETLAG", "Chandelier", "ZOO"]:
        if room.lower() in fold(venue_label):
            event["room"] = room
            break
    event["price"] = text(product, ".summary .price")
    event["description"] = text(product, ".woocommerce-product-details__short-description")[:400]
    if product.select_one(".out-of-stock"):
        event["availability"] = "sold_out"
    return [event]


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
