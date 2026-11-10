"""Official Cinéma Bellevaux weekly screening cards."""

import re
from datetime import date, timedelta
from urllib.parse import urljoin, urlparse

from agenda import fold
from bar_adapters import base_event
from venue_adapters import MONTHS, clock, set_start, text


def parse_bellevaux(soup, url):
    events = []
    for card in soup.select(".block-default"):
        link = card.select_one(".block-default-header a[href]")
        if not link:
            continue
        detail = urljoin(url, link["href"])
        if urlparse(detail).hostname != urlparse(url).hostname:
            continue
        period = re.match(r"^/(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{4})/", urlparse(detail).path)
        if not period:
            continue
        try:
            first = date(int(period[5]), int(period[2]), int(period[1]))
            last = date(int(period[5]), int(period[4]), int(period[3]))
            if not timedelta(0) <= last - first <= timedelta(days=7):
                continue  # ambiguous year boundary, not normalized by guessing
        except ValueError:
            continue
        schedule = fold(text(card, ".block-default-overtitle"))
        sessions = [(int(m[1]), int(m[2]), m[3]) for m in re.finditer(r"(\d{1,2})\.(\d{1,2})\s+a\s+(\d{1,2}:\d{2})", schedule)]
        for match in re.finditer(r"(\d{1,2})\s+(\w+)\s+a\s+(\d{1,2}:\d{2})", schedule):
            if match[2] in MONTHS:
                sessions.append((int(match[1]), MONTHS[match[2]], match[3]))
        for day_number, month, hour in sessions:
            try:
                day = date(first.year, month, day_number)
            except ValueError:
                continue
            if not first <= day <= last:
                continue
            event = base_event(text(card, "h3"), detail, url)
            if not event["title"]:
                continue
            event.update(location="Cinéma Bellevaux", municipality="Lausanne", event_kind="ScreeningEvent",
                         category="Cinéma", adapter="bellevaux-v1", series_id=detail,
                         date_basis="explicit programme-week URL + published session day/month")
            set_start(event, day, clock(hour))
            event["description"] = text(card, ".visible-xs")[:400]
            image = card.select_one(".block-default-img img[src]")
            event["image"] = urljoin(url, image["src"]) if image else ""
            events.append(event)
    return events
