"""Official programme pages for Pulloff Théâtres."""
import re
from datetime import date, timedelta

from agenda import fold
from venue_adapters import clock, set_start

from .common import event_at


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
