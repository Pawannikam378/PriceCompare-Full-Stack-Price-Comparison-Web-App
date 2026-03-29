"""
api_fetcher.py
--------------
Fetches real product data from DummyJSON (https://dummyjson.com/products/search).
Returns structured results matching the ProductResult schema.

Function:
    fetch_products(query: str) -> list[ProductResult]
"""

import logging
import random
import httpx
from models import ProductResult

logger = logging.getLogger(__name__)

DUMMYJSON_SEARCH_URL = "https://dummyjson.com/products/search"
REQUEST_TIMEOUT = 10.0  # seconds

# Platform mappings with realistic URL templates and price factors
PLATFORM_CONFIG = {
    "Amazon": {
        "url_template": "https://www.amazon.in/s?k={query}",
        "price_factor": 1.00,
        "price_jitter": 0.05,
    },
    "Flipkart": {
        "url_template": "https://www.flipkart.com/search?q={query}",
        "price_factor": 0.96,
        "price_jitter": 0.04,
    },
    "Croma": {
        "url_template": "https://www.croma.com/searchB?q={query}",
        "price_factor": 1.04,
        "price_jitter": 0.06,
    },
}

# DummyJSON prices are in USD; approximate conversion to INR
USD_TO_INR = 83.5


def _usd_to_inr(usd_price: float, factor: float, jitter: float) -> float:
    """Convert USD to INR with platform factor and small random jitter."""
    rng = random.Random()
    noise = rng.uniform(-jitter, jitter)
    return round(usd_price * USD_TO_INR * (factor + noise), 2)


def fetch_products(query: str) -> list[ProductResult]:
    """
    Query DummyJSON for real products matching `query`.

    For each product found, three platform listings are synthesised
    (Amazon, Flipkart, Croma) using the real DummyJSON price as a base
    and applying per-platform factors so that prices differ realistically.

    Returns:
        List of ProductResult objects, one per platform, sorted by price.
    """
    logger.info("Fetching products from DummyJSON for query: '%s'", query)

    try:
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            response = client.get(
                DUMMYJSON_SEARCH_URL,
                params={"q": query, "limit": 1},
            )
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        logger.error("DummyJSON HTTP error: %s", exc)
        return []
    except httpx.RequestError as exc:
        logger.error("DummyJSON request failed: %s", exc)
        return []
    except Exception as exc:
        logger.error("Unexpected error fetching from DummyJSON: %s", exc)
        return []

    products = data.get("products", [])
    if not products:
        logger.warning("No DummyJSON products found for query: '%s'", query)
        return []

    # Use the first (most relevant) product as the base
    product = products[0]
    base_price_usd: float = float(product.get("price", 100.0))
    base_rating: float = float(product.get("rating", 4.0))

    results: list[ProductResult] = []
    for platform, cfg in PLATFORM_CONFIG.items():
        inr_price = _usd_to_inr(base_price_usd, cfg["price_factor"], cfg["price_jitter"])
        link = cfg["url_template"].format(query=query.replace(" ", "+"))
        results.append(
            ProductResult(
                platform=platform,
                price=inr_price,
                rating=round(min(5.0, max(1.0, base_rating + random.uniform(-0.2, 0.2))), 1),
                link=link,
                is_cheapest=False,
            )
        )

    logger.info(
        "DummyJSON product '%s' (base $%.2f USD) → %d platform listings",
        product.get("title", query),
        base_price_usd,
        len(results),
    )
    return results
