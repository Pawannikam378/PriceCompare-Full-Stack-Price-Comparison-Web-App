"""
aggregator.py
-------------
Combines results from api_fetcher (real DummyJSON data), sorts by price (ascending),
and marks the cheapest option.

Falls back to simulated scrapers if the real API returns no results.
"""

import logging
from models import ProductResult, SearchResponse
from api_fetcher import fetch_products
from scrapers import scrape_amazon, scrape_flipkart, scrape_croma

logger = logging.getLogger(__name__)


def aggregate_results(query: str) -> SearchResponse:
    """
    Fetch real product listings from DummyJSON API, apply platform-specific
    pricing, sort by price, and mark the cheapest.

    Falls back to simulated scrapers if the real API is unavailable.

    Args:
        query: The product search term.

    Returns:
        A SearchResponse containing sorted results and the cheapest product.
    """
    logger.info("Aggregating results for query: '%s'", query)

    # Try real API first
    results: list[ProductResult] = fetch_products(query)

    # Fallback to simulated scrapers if real API returned nothing
    if not results:
        logger.warning(
            "Real API returned no results for '%s'. Falling back to simulated data.", query
        )
        raw: list[ProductResult | None] = [
            scrape_amazon(query),
            scrape_flipkart(query),
            scrape_croma(query),
        ]
        results = [r for r in raw if r is not None]

    if not results:
        logger.warning("No results returned for query: '%s'", query)
        return SearchResponse(query=query, results=[], cheapest=None)

    # Sort ascending by price
    results.sort(key=lambda r: r.price)

    # Mark the cheapest
    cheapest = results[0]
    cheapest.is_cheapest = True

    logger.info(
        "Cheapest for '%s': %s at ₹%s",
        query, cheapest.platform, cheapest.price
    )

    return SearchResponse(query=query, results=results, cheapest=cheapest)
