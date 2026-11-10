"""Public onsite calendars for bars and independent venues."""

import json
import re
from datetime import date, datetime, time, timedelta, timezone
from urllib.parse import urljoin, urlparse

import json5

from agenda import TZ, fold


def base_event(title, page_url, evidence_url):
    return dict(title=title, date="", time="", end_date="", location="", address="",
                category="Culture", subcategory="", description="", image="", price="",
                url=page_url, evidence_url=evidence_url, tags=[], featured=False)


def tacos_array(text):
    marker = re.search(r"window\.TACOS_EVENTS\s*=\s*\[", text)
    if marker:
        start = marker.end() - 1
    else:
        marker = re.search(r"window\.TACOS_EVENTS\s*=.*?\.concat\(\s*\[", text)
        if not marker:
            raise ValueError("Format du calendrier Taco's non reconnu")
        start = marker.end() - 1
    value, error, _ = json5.parse(text, start=start, consume_trailing=False)
    if error or not isinstance(value, list):
        raise ValueError("Calendrier Taco's invalide")
    return value


def parse_tacos(text, page_url, evidence_url):
    events = []
    kinds = {"live": ("MusicEvent", "Musique"), "dj": ("MusicEvent", "Clubbing"),
             "karaoke": ("Karaoke", "Musique"), "impro": ("ComedyEvent", "Humour")}
    for row in tacos_array(text):
        if not isinstance(row, dict):
            continue
        evt = base_event(row.get("title") or "Soirée privée", page_url, evidence_url)
        evt.update(date=row.get("date", ""), time=row.get("time", ""),
                   location="Taco’s Bar", municipality="Lausanne",
                   venue_basis="official_onsite_calendar", description=row.get("desc", ""),
                   price=row.get("price", ""), private=row.get("prive") is True,
                   event_status="EventCancelled" if row.get("annule") else "EventScheduled",
                   source_tag=row.get("tag", ""))
        evt["event_kind"], evt["category"] = kinds.get(fold(row.get("tag", "")), ("", "Culture"))
        image = row.get("img") or ""
        if isinstance(image, list):
            image = image[0] if image else ""
        evt["image"] = urljoin(page_url, image) if image else ""
        try:
            day = date.fromisoformat(evt["date"])
            start = datetime.combine(day, time.fromisoformat(evt["time"]), TZ)
            if start.astimezone(timezone.utc).astimezone(TZ).replace(tzinfo=None) != start.replace(tzinfo=None) or start.replace(fold=0).utcoffset() != start.replace(fold=1).utcoffset():
                raise ValueError("Heure locale ambiguë ou inexistante")
            evt["start_at"] = start.isoformat()
            if row.get("end"):
                end = datetime.combine(day, time.fromisoformat(row["end"]), TZ)
                if end < start:
                    end += timedelta(days=1)  # source calendar uses closing hours
                if end.astimezone(timezone.utc).astimezone(TZ).replace(tzinfo=None) != end.replace(tzinfo=None) or end.replace(fold=0).utcoffset() != end.replace(fold=1).utcoffset():
                    raise ValueError("Fin locale ambiguë ou inexistante")
                evt["end_at"] = end.isoformat()
                evt["end_date"] = end.date().isoformat()
        except (ValueError, TypeError):
            pass  # missing/invalid values are retained for review
        if row.get("end") and not evt.get("end_at"):
            evt["end_unverified"] = True
        events.append(evt)
    return events


def parse_captain(text, page_url, evidence_url):
    rows = json.loads(text)
    if not isinstance(rows, list):
        raise ValueError("Calendrier Captain Cook invalide")
    events = []
    for row in rows:
        if not isinstance(row, dict) or not row.get("title"):
            continue
        evt = base_event(row["title"], page_url, evidence_url)
        evt.update(start_at=row.get("start", ""), end_at=row.get("end", ""),
                   location="Captain Cook", municipality="Lausanne",
                   description=row.get("description", ""), price=row.get("price", ""),
                   source_tag=row.get("category", ""), source_type=row.get("type", ""),
                   # Many records use opening time 17h while descriptions say 19h.
                   time_role="unverified", editorial_verified=False)
        for field, target in [("start", "date"), ("end", "end_date")]:
            try:
                dt = datetime.fromisoformat(row.get(field, ""))
                if dt.tzinfo is None:
                    continue
                dt = dt.astimezone(TZ)
                evt[target] = dt.date().isoformat()
                if field == "start":
                    evt["time"] = dt.strftime("%H:%M")
            except (ValueError, TypeError):
                pass
        if row.get("image"):
            evt["image"] = urljoin(page_url, row["image"])
        evt["commercial_offer"] = fold(row.get("category", "")) in {"promo", "cocktails"}
        evt["programme_summary"] = fold(row.get("type", "")) in {"programme", "programe"}
        events.append(evt)
    return events


def collect_bar(url, soup, fetch):
    host = urlparse(url).hostname
    if host == "tacos-bar.ch":
        events = []
        scripts = [urljoin(url, s["src"]) for s in soup.select("script[src]")
                   if urlparse(urljoin(url, s["src"])).hostname == host
                   and urlparse(s["src"]).path.rsplit("/", 1)[-1] in {"events-data.js", "events-extra.php"}]
        if not scripts:
            raise ValueError("Fichiers publics du calendrier absents")
        for script in scripts:
            events.extend(parse_tacos(fetch(script), url, script))
        return events, "public-calendar (JSON5, sans exécution JS)"
    if host == "captaincook.ch":
        if not re.search(r'fetch\([\s]*["\']events\.php["\']', str(soup)):
            raise ValueError("Lien public events.php absent")
        feed = urljoin(url, "events.php")
        return parse_captain(fetch(feed), url, feed), "public-calendar (JSON, horaires à vérifier)"
    if host == "www.bruxellescafe.ch":
        events = []
        months = {m: i for i, m in enumerate(["janvier", "fevrier", "mars", "avril", "mai", "juin",
                  "juillet", "aout", "septembre", "octobre", "novembre", "decembre"], 1)}
        for card in soup.select("article.category-events"):
            heading = card.select_one("h2.entry-title a[href]")
            if not heading:
                continue
            link = urljoin(url, heading["href"])
            evt = base_event(heading.get_text(" ", strip=True), link, link)
            evt["location"] = "Bruxelles Café"
            evt["municipality"] = "Lausanne"
            desc = card.select_one(".post-data")
            evt["description"] = desc.get_text(" ", strip=True) if desc else ""
            match = re.search(r"[–—-]\s*(\d{1,2})(?:er)?\s+(\w+)\s+(\d{4})\s*$", fold(evt["title"]))
            if match and match[2] in months:
                try:
                    evt["date"] = date(int(match[3]), months[match[2]], int(match[1])).isoformat()
                except ValueError:
                    pass
            # No extraction of opening hours / guessed year / poster OCR.
            image = card.select_one("img[src]")
            evt["image"] = urljoin(url, image["src"]) if image else ""
            events.append(evt)
        return events, "official-articles (validation requise)"
    if host == "la-datcha.ch":
        events = []
        for heading in soup.select("h2.wp-block-post-title a[href]"):
            title = heading.get_text(" ", strip=True)
            if not re.match(r"^(lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|date reportee)\b", fold(title)):
                continue
            link = urljoin(url, heading["href"])
            evt = base_event(title, link, link)
            # Do not infer year from today's date, or venue from the footer:
            # the programme explicitly contains hors-les-murs evenings.
            evt["event_status"] = "EventPostponed" if fold(title).startswith("date reportee") else ""
            events.append(evt)
        return events, "official-programme (année, horaires et lieu à vérifier dans les détails)"
    return None
