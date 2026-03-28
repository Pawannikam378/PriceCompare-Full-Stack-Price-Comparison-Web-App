"""
scrapers.py
-----------
Simulated marketplace "scrapers" for Amazon, Flipkart, and Croma.

NOTE: In a real application these functions would call the respective
platform APIs or parse HTML. Here we generate realistic randomised
price/rating data so the application works without any external dependencies
or legal concerns around scraping.
"""

import random
import hashlib
import logging
from models import ProductResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _deterministic_seed(query: str, platform: str) -> int:
    """
    Derive a reproducible integer seed from query + platform so that the
    same search always returns similar (but slightly varied) prices.
    """
    raw = f"{query.lower().strip()}::{platform}"
    return int(hashlib.md5(raw.encode()).hexdigest(), 16) % (2 ** 32)


def _simulate_price(query: str, platform: str, base: float, spread: float) -> float:
    """Return a price that varies by ±spread around base, seeded by query."""
    seed = _deterministic_seed(query, platform)
    rng = random.Random(seed)
    variation = rng.uniform(-spread, spread)
    # Add a small additional random component so history changes over time
    live_variation = random.uniform(-spread * 0.1, spread * 0.1)
    return round(max(base + variation + live_variation, 100.0), 2)


def _simulate_rating(query: str, platform: str) -> float:
    seed = _deterministic_seed(query, platform) + 1
    rng = random.Random(seed)
    return round(rng.uniform(3.2, 5.0), 1)


# ---------------------------------------------------------------------------
# Product catalogue  (base prices per category keyword)
# ---------------------------------------------------------------------------

CATALOGUE: dict[str, dict] = {
    # keyword  : {base_price, spread}
    "iphone":   {"base": 79999,  "spread": 8000},
    "samsung":  {"base": 34999,  "spread": 6000},
    "laptop":   {"base": 54999,  "spread": 12000},
    "macbook":  {"base": 119999, "spread": 10000},
    "headphone":{"base": 4999,   "spread": 2000},
    "earbuds":  {"base": 3499,   "spread": 1500},
    "tablet":   {"base": 24999,  "spread": 5000},
    "watch":    {"base": 8999,   "spread": 3000},
    "tv":       {"base": 39999,  "spread": 10000},
    "camera":   {"base": 44999,  "spread": 8000},
    "keyboard": {"base": 2999,   "spread": 1000},
    "mouse":    {"base": 1499,   "spread": 500},
    "monitor":  {"base": 18999,  "spread": 4000},
    "speaker":  {"base": 6999,   "spread": 2500},
    "charger":  {"base": 1999,   "spread": 500},
    "default":  {"base": 14999,  "spread": 5000},
}

PLATFORM_CONFIG = {
    "Amazon": {
        "url_template": "https://www.amazon.in/s?k={query}",
        "price_factor": 1.00,
    },
    "Flipkart": {
        "url_template": "https://www.flipkart.com/search?q={query}",
        "price_factor": 0.97,   # Flipkart slightly cheaper on average
    },
    "Croma": {
        "url_template": "https://www.croma.com/searchB?q={query}",
        "price_factor": 1.04,   # Croma slightly higher (retail markup)
    },
}


def _resolve_catalogue(query: str) -> dict:
    """Find the best matching catalogue entry for the search query."""
    q = query.lower()
    for keyword, config in CATALOGUE.items():
        if keyword in q:
            return config
    return CATALOGUE["default"]


# ---------------------------------------------------------------------------
# Public scraper functions
# ---------------------------------------------------------------------------

def scrape_amazon(query: str) -> ProductResult | None:
    """Simulate an Amazon product search."""
    try:
        cfg = PLATFORM_CONFIG["Amazon"]
        cat = _resolve_catalogue(query)
        price = _simulate_price(query, "Amazon", cat["base"] * cfg["price_factor"], cat["spread"])
        rating = _simulate_rating(query, "Amazon")
        url = cfg["url_template"].format(query=query.replace(" ", "+"))
        logger.debug("Amazon  → ₹%s | ★%s", price, rating)
        return ProductResult(platform="Amazon", price=price, rating=rating, link=url)
    except Exception as exc:
        logger.error("Amazon scraper failed: %s", exc)
        return None


def scrape_flipkart(query: str) -> ProductResult | None:
    """Simulate a Flipkart product search."""
    try:
        cfg = PLATFORM_CONFIG["Flipkart"]
        cat = _resolve_catalogue(query)
        price = _simulate_price(query, "Flipkart", cat["base"] * cfg["price_factor"], cat["spread"])
        rating = _simulate_rating(query, "Flipkart")
        url = cfg["url_template"].format(query=query.replace(" ", "%20"))
        logger.debug("Flipkart → ₹%s | ★%s", price, rating)
        return ProductResult(platform="Flipkart", price=price, rating=rating, link=url)
    except Exception as exc:
        logger.error("Flipkart scraper failed: %s", exc)
        return None


def scrape_croma(query: str) -> ProductResult | None:
    """Simulate a Croma product search."""
    try:
        cfg = PLATFORM_CONFIG["Croma"]
        cat = _resolve_catalogue(query)
        price = _simulate_price(query, "Croma", cat["base"] * cfg["price_factor"], cat["spread"])
        rating = _simulate_rating(query, "Croma")
        url = cfg["url_template"].format(query=query.replace(" ", "%20"))
        logger.debug("Croma   → ₹%s | ★%s", price, rating)
        return ProductResult(platform="Croma", price=price, rating=rating, link=url)
    except Exception as exc:
        logger.error("Croma scraper failed: %s", exc)
        return None
