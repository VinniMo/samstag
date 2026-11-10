"""Public JavaScript calendar embedded by Arsenic."""
import json
import re
from datetime import datetime
from html import unescape

from agenda import fold
from venue_adapters import set_start

from .common import event_at


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
