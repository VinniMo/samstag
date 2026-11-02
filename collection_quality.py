"""Conservative validation and occurrence identity; no network or database."""
import hashlib
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

from agenda import TZ, fold
from config import config
from source_registry import VENUES, SOURCES, source_for

MUNICIPALITIES = {"lausanne", "pully", "prilly", "renens", "ecublens", "chavannes pres renens",
                  "crissier", "bussigny", "saint sulpice", "st sulpice", "epalinges", "le mont sur lausanne"}
EVENT_KINDS = {"MusicEvent", "ComedyEvent", "DanceEvent", "Karaoke", "TheaterEvent", "ScreeningEvent", "Festival", "ClubNight", "BlindTest", "OpenMic"}


def normalized(value):
    return " ".join(re.findall(r"\w+", fold(value)))


def venue_for(name):
    key = normalized(name)
    if not key:
        return None
    aliases = {"D! Club": ["D! Club Lausanne"], "Jumeaux Jazz Club": ["Jumeaux", "Jumeaux Jazz"],
               "Les Docks": ["Docks", "Docks - Lausanne"], "Barberousse": ["Barberousse Lausanne"],
               "DIFF": ["Le Diff bar", "DIFF bar"], "Cave du Bleu Lézard": ["Bleu Lézard"],
               "Brasserie du Château / Château Music Club": ["Château Music Club", "Brasserie du Château"],
               "Le Pavillon / Pavillon Bar & Kitchen": ["Le Pavillon", "Pavillon Bar & Kitchen"],
               "La Bossette": ["À la Bossette", "A la Bossette"]}
    for bar in VENUES:
        names = [bar["nom"], *bar["nom"].split(" / "), *aliases.get(bar["nom"], [])]
        if any(key == normalized(n) for n in names):
            return bar
    return None


def occurrence_id(event):
    """No fuzzy merge: same title, canonical place, date AND explicit time."""
    parts = [normalized(event.get("title", "")), event.get("venue_id", ""),
             event.get("date", ""), event.get("time", "")]
    if not parts[1] or not parts[2] or not parts[3]:
        # Uncertain records from distinct pages must not overwrite each other.
        parts.append(event.get("evidence_url", "") or event.get("url", ""))
        parts.append(normalized(event.get("location", "")))
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:24]


def assess(raw, source, now=None):
    now = now or datetime.now(TZ)
    event = dict(raw)
    event["source_url"] = source
    event["checked_at"] = now.isoformat()
    venue = venue_for(event.get("location", ""))
    event["venue_id"] = venue["id"] if venue else ""
    event["id"] = occurrence_id(event)

    def decision(status, reason):
        return {"event": event, "status": status, "reason": reason}

    if "buzz club" in normalized(event.get("location", "")):
        return decision("excluded", "excluded_venue")
    if event.get("private"):
        return decision("excluded", "private_event")
    if event.get("commercial_offer") or event.get("programme_summary"):
        return decision("excluded", "commercial_offer_or_programme_summary")
    if event.get("event_status") == "EventCancelled":
        return decision("excluded", "cancelled")
    if event.get("event_status") in {"EventPostponed", "EventRescheduled"}:
        return decision("review", "changed_schedule")
    if event.get("schedule_conflict"):
        return decision("review", "conflicting_published_dates")
    if not venue:
        return decision("review", "unverified_or_out_of_scope_venue")
    if venue.get("selection_nocturne") == "Hors périmètre":
        return decision("excluded", "venue_out_of_scope")
    if venue.get("selection_nocturne") != "Retenu":
        return decision("review", "venue_requires_editorial_review")
    # A Lausanne bar can organize away events: source address is never enough.
    if normalized(event.get("municipality", "")) not in MUNICIPALITIES:
        return decision("review", "unverified_event_municipality")
    # An aggregator must never bypass the official collector's review gates.
    tourism = lambda url: (urlparse(url or "").hostname or "").lower() in {
        "lausanne-tourisme.ch", "www.lausanne-tourisme.ch"}
    if any(tourism(event.get(key)) for key in ("url", "evidence_url")) or tourism(source):
        if any(s.get("enabled") and s.get("type") == "official"
               and s.get("venue_id") == venue["id"] for s in SOURCES):
            return decision("review", "official_source_required_for_covered_venue")
    channel = source_for(source)
    if not event.get("address") and channel and channel.get("venue_id") == venue["id"] and venue.get("adresse_statut") == "Confirmée":
        event["address"] = venue.get("adresse", "")
        event["address_proof"] = venue.get("preuve", "")
    if event.get("event_kind") not in EVENT_KINDS:
        return decision("review", "editorial_type_requires_review")
    evidence = event.get("evidence_url", "")
    if urlparse(evidence).scheme not in {"https", "http"}:
        return decision("review", "missing_event_evidence")
    try:
        start = datetime.fromisoformat(event.get("start_at", "").replace("Z", "+00:00"))
        if start.tzinfo is None:
            return decision("review", "unverified_timezone")
        start = start.astimezone(TZ)
        end = datetime.fromisoformat(event["end_at"].replace("Z", "+00:00")) if event.get("end_at") else None
        if end and (end.tzinfo is None or end < start):
            return decision("review", "invalid_end")
    except (ValueError, TypeError):
        return decision("review", "missing_or_invalid_start")
    if not event.get("time"):
        return decision("review", "missing_start_time")
    if event.get("date") != start.date().isoformat() or event["time"] != start.strftime("%H:%M"):
        return decision("review", "inconsistent_start_fields")
    if event.get("time_role") == "unverified":
        return decision("review", "unverified_start_time")
    if event.get("end_unverified"):
        return decision("review", "unverified_end_time")
    if event.get("time_role") == "doors" and event.get("event_kind") != "ClubNight":
        return decision("review", "doors_not_artistic_start")
    # A multi-day programme needs individual dated occurrences, not an interval.
    if end and end - start > timedelta(hours=18):
        return decision("review", "multi_day_programme_needs_occurrences")
    if (end and end <= now) or (not end and start.date() < now.date()):
        return decision("excluded", "past")
    if start < now and not end:
        return decision("review", "already_started_unknown_end")
    if start > now + timedelta(days=config.COLLECTION_HORIZON_DAYS):
        return decision("review", "outside_collection_horizon")
    if event.get("event_status") not in {"", None, "EventScheduled"}:
        return decision("review", "unknown_event_status")
    if channel and channel.get('require_detail_confirmation') and not event.get('detail_confirmed'):
        return decision('review', 'missing_detail_confirmation')
    confirmed_dclub_concert = (channel and channel.get("id") == "SRC_L003"
                               and event.get("event_kind") == "MusicEvent"
                               and event.get("artistic_time_confirmed")
                               and event.get("time_role") == "start"
                               and urlparse(event.get("start_evidence_url", "")).hostname == "visaevents.swoogo.com")
    if channel and channel.get("allowed_kinds") and event.get("event_kind") not in channel["allowed_kinds"] and not confirmed_dclub_concert:
        return decision("review", "source_type_not_qualified")
    return decision("candidate", "ready_for_first_source_validation")


def publicly_visible(item, now=None):
    """Only reviewed, recently checked records can enter the public API."""
    if item["status"] != "approved":
        return False
    now = now or datetime.now(TZ)
    if item.get("reason") == "qualified_source_complete_event":
        source = source_for(item["event"].get("source_url"))
        if not source or not source.get("auto_publish"):
            return False
    try:
        checked = datetime.fromisoformat(item["event"]["checked_at"])
        if checked.tzinfo is None or not timedelta(0) <= now - checked <= timedelta(hours=24):
            return False
    except (ValueError, KeyError):
        return False
    return assess(item["event"], item["event"]["source_url"], now)["status"] == "candidate"
