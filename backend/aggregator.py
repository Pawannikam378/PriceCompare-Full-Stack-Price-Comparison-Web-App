"""
aggregator.py
-------------
Combines results from all marketplace scrapers, sorts by price (ascending),
and marks the cheapest option.
"""

import logging
from models import ProductResult, SearchResponse
from scrapers import scrape_amazon, scrape_flipkart, scrape_croma

logger = logging.getLogger(__name__)


def aggregate_results(query: str) -> SearchResponse:
    """
    Run all scrapers concurrently (simulated sequentially here since they're
    in-memory), filter out failures, sort by price, and mark cheapest.

    Args:
        query: The product search term.

    Returns:
        A SearchResponse containing sorted results and the cheapest product.
    """
    logger.info("Aggregating results for query: '%s'", query)

    # Gather results from each platform
    raw_results: list[ProductResult | None] = [
        scrape_amazon(query),
        scrape_flipkart(query),
        scrape_croma(query),
    ]

    # Filter failures
    results: list[ProductResult] = [r for r in raw_results if r is not None]

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
