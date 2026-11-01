"""Read the same public external endpoint as an establishment's embedded widget.

Only widget identifiers actually published in the official page are used.
No account, session credential, administrative API or recurrence inference.
"""
import json
import re
from datetime import datetime
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from agenda import TZ
from bar_adapters import base_event
from collection_quality import normalized
from source_registry import VENUES, source_for
from collection_result import CollectionResult

API = "https://api.hango.ch/api/v1/external"
MAX_PAGES = 12
KINDS = {"dj set": ("MusicEvent", "Clubbing"), "concert": ("MusicEvent", "Musique"),
         "live music": ("MusicEvent", "Musique"), "karaoke": ("Karaoke", "Musique"),
         "blind test": ("BlindTest", "Musique"), "stand up": ("ComedyEvent", "Humour"),
         "open mic": ("OpenMic", "Musique"), "spectacle d improvisation": ("TheaterEvent", "Théâtre")}


def parse_events(data, source, venue, evidence_url):
    result = []
    for row in data.get("nodes", []):
        if not isinstance(row, dict) or not row.get("name"):
            continue
        event = base_event(row["name"], source["canal"], evidence_url)
        event.update(location=venue["nom"], municipality=venue["commune"],
                     start_at=row.get("startsAt", ""), end_at=row.get("endsAt", ""),
                     source_event_key="hango:"+row["id"], series_id=row.get("rootEventId"), adapter="hango-public-v1")
        event["description"] = BeautifulSoup(row.get("description") or "", "lxml").get_text(" ", strip=True)[:400]
        terms = row.get("eventTagTerms") or {}
        types = [normalized(term.get("tagTerm", {}).get("name", "")) for term in terms.get("EVENT_TYPE", [])]
        event["source_types"] = types
        for kind in types:
            if kind in KINDS:
                event["event_kind"], event["category"] = KINDS[kind]
                break
        if "soiree a theme" in types and terms.get("MUSIC"):
            event.update(event_kind="ClubNight", category="Clubbing")
        # Music genre alone does not establish that an afterwork or food offer
        # is a concert. Unmapped thematic evenings remain for editorial review.
        event["commercial_offer"] = any(t in {"happy hour", "offre speciale", "promotion"} for t in types)
        images = [m for m in row.get("eventMediaAssets", []) if m.get("type") == "IMAGE" and m.get("url")]
        if images:
            event["image"] = min(images, key=lambda m: m.get("order", 0))["url"]
        for field, target in [("startsAt", "date"), ("endsAt", "end_date")]:
            try:
                value = datetime.fromisoformat((row.get(field) or "").replace("Z", "+00:00"))
                if value.tzinfo is None:
                    continue
                value = value.astimezone(TZ)
                event[target] = value.date().isoformat()
                if field == "startsAt":
                    event["time"] = value.strftime("%H:%M")
            except (ValueError, TypeError):
                continue
        low, high = row.get("minPrice"), row.get("maxPrice")
        if low is not None:
            event["price"] = "CHF " + str(low)
            if high is not None and high != low:
                event["price"] += "–" + str(high)
        elif high is not None and str(high) in {"0", "0.00", "0.0"}:
            event["price"] = "Gratuit"
        result.append(event)
    return result


def collect_hango(url, soup, fetch):
    widgets = [node["src"] for node in soup.select("iframe[src]")
               if urlparse(node["src"]).hostname == "backoffice.hango.ch"
               and re.fullmatch(r"/external/widgets/estb_live_[a-z0-9]+", urlparse(node["src"]).path)]
    if not widgets:
        return None
    source = source_for(url)
    if not source or not source.get("widget_names"):
        return [], "hango-public: identité du widget à qualifier"
    venue = next(v for v in VENUES if v["id"] == source["venue_id"])
    if len(set(widgets)) != 1:
        raise ValueError("Plusieurs calendriers publics : attribution à vérifier")
    key = urlparse(widgets[0]).path.rsplit("/", 1)[-1]
    headers = {"x-api-key": key}
    identity = json.loads(fetch(API+"/establishment", extra_headers=headers))
    if not identity.get("success") or normalized(identity.get("data", {}).get("name", "")) not in {normalized(n) for n in source["widget_names"]}:
        raise ValueError("Identité du calendrier différente de l’établissement attendu")
    events, total_pages = [], 0
    for page in range(1, MAX_PAGES+1):
        endpoint = API+f"/events?page={page}&hasOccurred=false"
        response = json.loads(fetch(endpoint, extra_headers=headers))
        if not response.get("success") or not isinstance(response.get("data"), dict):
            raise ValueError("Réponse du calendrier public invalide")
        data = response["data"]
        events.extend(parse_events(data, source, venue, widgets[0]))
        total_pages = data.get("pageInfo", {}).get("totalPages", 0)
        if not data.get("pageInfo", {}).get("hasNextPage"):
            break
    complete = not data.get("pageInfo", {}).get("hasNextPage", True)
    return CollectionResult(events, f"hango-public-v1: {page}/{total_pages} pages ; calendrier officiel intégré", complete)
