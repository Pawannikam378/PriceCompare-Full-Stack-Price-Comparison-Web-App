"""
main.py
-------
FastAPI application entry point.

Endpoints:
  GET /              – health check
  GET /search?query= – compare prices from real API across platforms
  GET /history?product= – returns price history from the database
  GET /predict?product= – AI-powered price prediction (Linear Regression)

Run with:
  uvicorn main:app --reload
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, save_product, get_price_history
from aggregator import aggregate_results
from models import SearchResponse, HistoryResponse, PriceHistoryEntry, PredictionResponse
from ml_model import predict_price

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
    description=(
        "Compare real product prices across Amazon, Flipkart and Croma "
        "with price history tracking and AI-powered price prediction."
    ),
    version="2.0.0",
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
    return {"status": "ok", "message": "PriceCompare API v2 is running."}


@app.get("/search", response_model=SearchResponse, tags=["Search"])
async def search(
    query: str = Query(..., min_length=1, max_length=200, description="Product name to search"),
):
    """
    Search for a product across all marketplaces using real DummyJSON API.

    - Fetches real product data and derives platform-specific prices.
    - Sorts results by price (ascending).
    - Marks the cheapest option.
    - Persists each result to the database for history tracking.
    """
    logger.info("Search request: '%s'", query)

    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        response = aggregate_results(query.strip())
    except Exception as exc:
        logger.exception("Aggregator error for query '%s': %s", query, exc)
        raise HTTPException(status_code=500, detail="Failed to fetch price data.") from exc

    # Persist results to DB (errors are logged, not raised)
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


@app.get("/predict", response_model=PredictionResponse, tags=["AI Prediction"])
async def predict(
    product: str = Query(..., min_length=1, max_length=200, description="Product name for price prediction"),
):
    """
    Predict the next price for a product using AI (Linear Regression).

    - Reads historical price data from the database.
    - Trains a Linear Regression model on price vs. time index.
    - Returns the predicted next price and trend direction (UP/DOWN/STABLE).
    - Returns a message if insufficient history data is available.

    Tip: Search for a product multiple times to build up history, then call /predict.
    """
    logger.info("Predict request: '%s'", product)

    try:
        result = predict_price(product.strip())
    except Exception as exc:
        logger.exception("Prediction error for '%s': %s", product, exc)
        raise HTTPException(status_code=500, detail="Failed to run price prediction.") from exc

    if result is None:
        return PredictionResponse(
            product=product,
            predicted_price=None,
            trend=None,
            message=(
                "Not enough price history to make a prediction. "
                "Search for this product a few times first to build up history."
            ),
        )

    return PredictionResponse(
        product=product,
        predicted_price=result["predicted_price"],
        trend=result["trend"],
        message=None,
    )
