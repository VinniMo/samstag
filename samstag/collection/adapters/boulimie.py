"""Official performance pages for Théâtre Boulimie."""
import re
from datetime import date, timedelta

from agenda import fold
from venue_adapters import MONTHS, clock, set_start, text

from .common import event_at, french_day


def parse_boulimie(soup, url):
    artist, subtitle = text(soup, "h1.show-artist"), text(soup, "h2.show-title")
    if not artist:
        return []
    title = " — ".join(filter(None, [artist, subtitle]))
    schedule = text(soup, ".show-schedule")
    description = text(soup, ".normal-text")
    # Touring and off-site productions must not inherit the theatre address.
    if any(w in fold(description) for w in ["n'ont pas lieu", "hors-les-murs", "hors les murs", "studios de la rts"]):
        event = event_at(title, url, url, "", "ComedyEvent", "Humour")
        event["description"] = description[:400]
        return [event]
    found = re.fullmatch(r"(\d{1,2})\s+au\s+(\d{1,2})\s+(\w+)\s+(\d{4})", fold(schedule))
    dates = []
    if found and found[3] in MONTHS:
        begin = date(int(found[4]), MONTHS[found[3]], int(found[1]))
        end = date(int(found[4]), MONTHS[found[3]], int(found[2]))
        if timedelta(0) <= end-begin <= timedelta(days=62):
            dates = [begin+timedelta(days=n) for n in range((end-begin).days+1)]
    else:
        day = french_day(schedule)
        if day:
            dates = [day]
    weekday_names = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    hours = {}
    for block in soup.select(".normal-text h6"):
        for line in block.get_text("\n", strip=True).splitlines():
            if ":" not in line:
                continue
            days, value = fold(line).split(":", 1)
            hour = clock(value)
            if hour:
                for index, name in enumerate(weekday_names):
                    if re.search(r"\b"+name+r"\b", days):
                        hours[index] = hour
    events = []
    for day in dates:
        if day.weekday() not in hours:
            continue
        event = event_at(title, url, url, "Théâtre Boulimie", "ComedyEvent", "Humour")
        set_start(event, day, hours[day.weekday()])
        event["description"] = description[:400]
        events.append(event)
    if not events:
        event = event_at(title, url, url, "Théâtre Boulimie", "ComedyEvent", "Humour")
        event["description"] = description[:400]
        events.append(event)
    return events
