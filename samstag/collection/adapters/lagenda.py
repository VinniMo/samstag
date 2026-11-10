"""Filtered regional listings from the L'Agenda aggregator."""

from datetime import datetime, timedelta
import re
from urllib.parse import urlencode, urljoin

from bs4 import BeautifulSoup

from agenda import TZ, fold
from collection_result import CollectionResult
from config import config
from venue_adapters import clock, dotted_day, set_start, text

from .common import event_at


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
            events.extend(rows)
            checks += 1
            pages = [a.get_text(strip=True) for a in listing.select('.em-pagination a[title]')]
            if str(page_number+1) not in pages:
                break
            if page_number == config.MAX_AGENDA_PAGES:
                truncated = True
    return CollectionResult(events, f"lagenda-filtered-v3: {checks} pages contrôlées, maximum {config.MAX_AGENDA_PAGES} par région (sélection filtrée)", partial=truncated)
