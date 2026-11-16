"""HTTP client for programme sources."""
import requests

from config import config


class FetchError(Exception):
    pass


def _fetch(url: str, extra_headers: dict | None = None) -> str:
    headers = {
        "User-Agent": config.SCRAPE_USER_AGENT,
        "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.5",
    }
    headers.update(extra_headers or {})
    try:
        resp = requests.get(url, headers=headers, timeout=config.SCRAPE_TIMEOUT_SECONDS)
        resp.raise_for_status()
        # Several venue servers omit charset and requests otherwise uses Latin-1.
        if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
            resp.encoding = resp.apparent_encoding or "utf-8"
        return resp.text
    except requests.RequestException as exc:
        raise FetchError(str(exc)) from exc
