"""Official MAD ticket product pages linked from the club agenda."""
import re
from datetime import date

from agenda import fold
from venue_adapters import MONTHS, clock, set_start, text

from .common import event_at


def parse_mad_ticket(soup, url):
    product = soup.select_one(".product")
    if not product:
        raise ValueError("Fiche de billetterie MAD absente")
    content = product.get_text(" ", strip=True)
    # Limit parsing to the product, never related-event cards or page footer.
    title = text(product, ".product_title")
    event = event_at(title, url, url, "MAD Club", "ClubNight", "Clubbing")
    event.update(source_event_key=url, time_role="doors")
    month_names = {**MONTHS, **{k[:3]: v for k, v in MONTHS.items()}}
    date_label = text(product, ".summary > h3") or title
    found = re.search(r"\b(\d{1,2})\s+(\w+)\s+(\d{4})\b", fold(date_label))
    day = None
    if found and found[2] in month_names:
        day = date(int(found[3]), month_names[found[2]], int(found[1]))
    start = re.search(r"ouverture des portes\s*:?\s*(\d{1,2}h\d{0,2})", fold(content))
    set_start(event, day, clock(start[1]) if start else None)
    # A MAD shop also sells Montreux, boat and other off-site events.
    summary_title = product.select_one('.summary > h1')
    details = summary_title.find_next_sibling('div') if summary_title else None
    venue_label = details.get_text(" ", strip=True) if details else content
    if not re.search(r"\b(?:mad\s+(?:mainfloor|jetlag|club)|jetlag)\b", fold(venue_label)) or "montreux" in fold(title):
        event.update(location="", municipality="")
    for room in ["Mainfloor", "JETLAG", "Chandelier", "ZOO"]:
        if room.lower() in fold(venue_label):
            event["room"] = room
            break
    event["price"] = text(product, ".summary .price")
    event["description"] = text(product, ".woocommerce-product-details__short-description")[:400]
    if product.select_one(".out-of-stock"):
        event["availability"] = "sold_out"
    return [event]
