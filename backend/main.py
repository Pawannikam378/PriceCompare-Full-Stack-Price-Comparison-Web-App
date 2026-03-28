"""
main.py
-------
FastAPI application entry point.

Endpoints:
  GET /search?query=<product>   – returns sorted price results from all platforms
  GET /history?product=<name>   – returns price history from the database

Run with:
  uvicorn main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, save_product, get_price_history
from aggregator import aggregate_results
from models import SearchResponse, HistoryResponse, PriceHistoryEntry

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise database on startup."""
    logger.info("Starting PriceCompare API …")
    init_db()
    yield
    logger.info("Shutting down PriceCompare API.")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PriceCompare API",
    description="Compare product prices across Amazon, Flipkart and Croma with history tracking.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS – allow the React dev server (and any origin in dev)
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
async def root():
    """Health-check endpoint."""
    return {"status": "ok", "message": "PriceCompare API is running."}


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search(
    query: str = Query(..., min_length=1, max_length=200, description="Product name to search"),
):
    """
    Search for a product across all marketplaces.

    - Simulates price fetch from Amazon, Flipkart, Croma.
    - Sorts results by price (ascending).
    - Marks the cheapest option.
    - Persists each result to the database (with same-session dedup).
    """
    logger.info("Search request: '%s'", query)

    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        response = aggregate_results(query.strip())
    except Exception as exc:
        logger.exception("Aggregator error for query '%s': %s", query, exc)
        raise HTTPException(status_code=500, detail="Failed to fetch price data.") from exc

    # Persist results to DB (non-blocking; errors are logged, not raised)
    for result in response.results:
        try:
            save_product(query.strip(), result.platform, result.price)
        except Exception as exc:
            logger.warning("Could not save product to DB: %s", exc)

    return response


@app.get("/history", response_model=HistoryResponse, tags=["History"])
async def history(
    product: str = Query(..., min_length=1, max_length=200, description="Product name to look up"),
):
    """
    Retrieve aggregated price history for a product.

    Returns daily average prices grouped by platform, sorted by date.
    Also includes computed lowest / highest prices across all history.
    """
    logger.info("History request: '%s'", product)

    try:
        rows = get_price_history(product.strip())
    except Exception as exc:
        logger.exception("DB error for history query '%s': %s", product, exc)
        raise HTTPException(status_code=500, detail="Failed to fetch price history.") from exc

    if not rows:
        return HistoryResponse(
            product=product,
            history=[],
            lowest_price=None,
            highest_price=None,
        )

    history_entries = [
        PriceHistoryEntry(date=r["date"], price=r["price"], platform=r.get("platform"))
        for r in rows
    ]

    prices = [e.price for e in history_entries]
    return HistoryResponse(
        product=product,
        history=history_entries,
        lowest_price=min(prices),
        highest_price=max(prices),
    )
