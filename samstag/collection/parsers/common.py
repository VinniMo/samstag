"""Shared normalization for generic programme parsers."""
import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo


LOCAL_TZ = ZoneInfo("Europe/Zurich")

CATEGORY_RULES: dict[str, tuple[str, ...]] = {
    # Order matters — first match wins. Clubbing before Musique to catch DJ/techno.
    "Clubbing":  ("techno", "house", "club night", "after", "rave", "warehouse",
                  "underground", "boiler room", "dj set", "afterhour", "all night",
                  "d! club", "mad club", "folklore", "datcha"),
    "Musique":   ("concert", "jazz", "rock", "classique", "opéra", "orchestre",
                  "récital", "électronique", "electro", "dj", "chanson", "vivaldi",
                  "beethoven", "brahms", "verdi", "live band", "punk", "metal",
                  "indie", "pop", "folk", "hip-hop", "rap"),
    "Théâtre":   ("théâtre", "pièce", "comédie", "tragédie", "hamlet",
                  "molière", "mise en scène", "spectacle", "monologue"),
    "Exposition": ("exposition", "expo", "vernissage", "galerie",
                   "rétrospective", "musée", "installation"),
    "Cinéma":    ("cinéma", "film", "projection", "documentaire",
                  "court-métrage", "ciné", "avant-première"),
    "Danse":     ("danse", "ballet", "chorégraphie", "flamenco",
                  "contemporain", "performance"),
    "Festival":  ("festival", "fête", "nuit des musées", "open air"),
    "Famille":   ("famille", "enfants", "jeune public", "marionnettes"),
    "Conférence": ("conférence", "débat", "symposium", "lecture", "talk"),
    "Sport":     ("sport", "marathon", "course", "match", "tournoi"),
    "Humour":    ("humour", "comedy", "stand-up", "one-man-show"),
    "Atelier":   ("atelier", "workshop", "initiation"),
    "Marché":    ("marché", "foire", "artisanat"),
}


def _gen_id(title: str, date: str) -> str:
    return hashlib.md5(f"{title}|{date}".encode("utf-8")).hexdigest()[:10]


def categorize(title: str, description: str = "") -> str:
    text = f"{title} {description}".lower()
    for category, keywords in CATEGORY_RULES.items():
        if any(kw in text for kw in keywords):
            return category
    return "Culture"


def _parse_iso_date(value: str) -> tuple[str, str]:
    if not value:
        return "", ""
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value[:10], ""
    if dt.tzinfo is not None:
        dt = dt.astimezone(LOCAL_TZ)
    # A bare date ("2026-10-16") carries no time: do not show "00:00".
    has_time = "T" in value or " " in value.strip()
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M") if has_time else ""
