"""Event extraction from iCalendar feeds."""
import re

from .common import _gen_id, _parse_iso_date, categorize


def _unfold_ics(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def _ics_value(value: str) -> str:
    return (value.replace("\\n", " ").replace("\\N", " ").replace("\\,", ",")
            .replace("\\;", ";").replace("\\\\", "\\").strip())


def _ics_date(key: str, value: str) -> tuple[str, str]:
    """DTSTART / DTEND: date-only, local, or UTC (Z) values."""
    value = value.strip()
    if "VALUE=DATE" in key and len(value) == 8:
        return f"{value[:4]}-{value[4:6]}-{value[6:]}", ""
    m = re.match(r"(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})\d{0,2}(Z?))?$", value)
    if not m:
        return "", ""
    y, mo, d, hh, mm, utc = m.groups()
    if hh is None:
        return f"{y}-{mo}-{d}", ""
    iso = f"{y}-{mo}-{d}T{hh}:{mm}:00" + ("+00:00" if utc else "")
    return _parse_iso_date(iso)


def parse_ics(text: str, page_url: str = "") -> list[dict]:
    """Read VEVENT entries from an iCalendar feed."""
    events: list[dict] = []
    current: dict[str, str] | None = None
    for line in _unfold_ics(text):
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT" and current is not None:
            title = _ics_value(current.get("SUMMARY", ""))
            date, time_str = current.get("_start", ("", ""))
            end_date, _ = current.get("_end", ("", ""))
            if title:
                description = _ics_value(current.get("DESCRIPTION", ""))[:400]
                location = _ics_value(current.get("LOCATION", ""))
                venue, _, address = location.partition(",")
                events.append({
                    "id": _gen_id(title, date), "title": title, "date": date,
                    "time": time_str, "end_date": end_date if end_date != date else "",
                    "location": venue.strip(), "address": address.strip(),
                    "category": categorize(title, description), "subcategory": "",
                    "description": description, "image": "", "price": "",
                    "url": current.get("URL", "").strip() or page_url,
                    "tags": [], "featured": False,
                })
            current = None
        elif current is not None and ":" in line:
            key, _, value = line.partition(":")
            name = key.split(";")[0].upper()
            if name == "DTSTART":
                current["_start"] = _ics_date(key, value)
            elif name == "DTEND":
                current["_end"] = _ics_date(key, value)
            else:
                current[name] = value
    return events
