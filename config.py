"""Application configuration loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Immutable application configuration."""

    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "5000"))
    DEBUG: bool = os.environ.get("FLASK_DEBUG", "1") == "1"
    DEMO_ENABLED: bool = os.environ.get("DEMO_ENABLED", "0") == "1"
    COLLECTION_ON_VISIT: bool = os.environ.get("COLLECTION_ON_VISIT", "1") == "1"
    COLLECTION_WORKERS: int = max(1, min(6, int(os.environ.get("COLLECTION_WORKERS", "4"))))
    COLLECTION_HORIZON_DAYS: int = max(14, min(365, int(os.environ.get("COLLECTION_HORIZON_DAYS", "90"))))

    DB_PATH: str = os.environ.get(
        "SAMSTAG_DB",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.db"),
    )

    SCRAPE_INTERVAL_SECONDS: int = int(os.environ.get("SCRAPE_INTERVAL", "3600"))
    SCRAPE_TIMEOUT_SECONDS: int = int(os.environ.get("SCRAPE_TIMEOUT", "12"))
    COLLECTION_LOG_RETENTION_DAYS: int = max(
        7, min(365, int(os.environ.get("COLLECTION_LOG_RETENTION_DAYS", "90")))
    )
    SCRAPE_USER_AGENT: str = os.environ.get(
        "SCRAPE_USER_AGENT",
        "Mozilla/5.0 (compatible; Samstag/1.0; +https://github.com/VinniMo/samstag)",
    )

    # ----- Tier 1: aggregators (broad coverage, few sources) -----
    SCRAPE_AGGREGATORS: tuple[str, ...] = (
        "https://agenda.lausanne.ch/",
        "https://www.lausanne.ch/vie-pratique/culture-et-loisirs/agenda.html",
        "https://ra.co/events/ch/lausanne",
        "https://shotgun.live/fr/cities/lausanne",
        "https://plateforme10.ch/agenda",
        # Regroupent aussi des bars et petits lieux (Barberousse, Jumeaux,
        # Romandie...). Adresses trouvées par recherche, à confirmer avec
        # /api/sources une fois en ligne.
        "https://www.lausanne-tourisme.ch/fr/evenement/",
        "https://www.guidle.com/fr/evenements/lausanne",
    )

    # Listing pages whose events live on their own pages: follow the links
    # whose path matches the pattern and read each page's JSON-LD.
    DETAIL_LINK_PATTERNS: tuple[tuple[str, str], ...] = (
        ("lausanne-tourisme.ch", r"^/fr/evenement/[a-z0-9-]+/?$"),
        ("guidle.com", r"^/fr/evenements/[^/]+_[A-Za-z0-9]+/?$"),
    )
    MAX_DETAIL_PAGES: int = int(os.environ.get("MAX_DETAIL_PAGES", "40"))
    MAX_AGENDA_PAGES: int = max(1, min(40, int(os.environ.get("MAX_AGENDA_PAGES", "20"))))

    # ----- Tier 2: venue-specific (alternative & niche scenes) -----
    SCRAPE_VENUES: tuple[str, ...] = (
        # Théâtre & danse
        "https://vidy.ch/programme",
        "https://arsenic.ch/saison",
        "https://tkm.ch/saison",
        "https://www.theatredebeaulieu.ch/programme",
        "https://www.theatre-octogone.ch/saison",
        # Concerts & alternatif
        "https://lesdocks.ch/agenda",
        "https://leromandie.ch/programme",
        "https://le-bourg.ch/programme",
        "https://www.chorus.ch/agenda",
        "https://casinodemontbenon.ch/agenda",
        # Clubbing
        "https://dclub.ch/events",
        "https://mad.ch/agenda",
        "https://folklore-club.ch/events",
        # Musique classique
        "https://www.opera-lausanne.ch/saison",
        "https://www.ocl.ch/concerts",
        # Musées
        "https://www.mcba.ch/expositions",
        "https://elysee.ch/expositions",
        "https://mudac.ch/expositions",
        "https://www.fondation-hermitage.ch/expositions",
        # Cinéma
        "https://www.cinematheque.ch/programme",
        "https://www.cinemabellevaux.ch/programme",
        "https://zinema.ch/programme",
    )

    @property
    def SCRAPE_SOURCES(self) -> tuple[str, ...]:
        """Qualified channels from the consolidated nightlife inventory."""
        from source_registry import active_sources
        return tuple(row["canal"] for row in active_sources())

    CATEGORIES: tuple[str, ...] = (
        "Musique", "Théâtre", "Exposition", "Cinéma", "Danse",
        "Festival", "Famille", "Conférence", "Sport", "Humour",
        "Atelier", "Marché", "Clubbing",
    )


config = Config()
