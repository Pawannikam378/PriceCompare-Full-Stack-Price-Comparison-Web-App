"""
ml_model.py
-----------
AI Price Prediction using Linear Regression.

Given a product name, this module:
 1. Reads its historical price data from the database.
 2. Fits a simple Linear Regression model on price vs. time index.
 3. Predicts the next price point.
 4. Returns the predicted price and a trend direction ("UP" / "DOWN" / "STABLE").

Public API:
    predict_price(product_name: str) -> dict | None
    Returns: {"predicted_price": float, "trend": str}
    Returns None if insufficient history.
"""

import logging
import numpy as np
from sklearn.linear_model import LinearRegression
from database import get_price_history

logger = logging.getLogger(__name__)

MIN_DATA_POINTS = 2  # minimum history entries required for a prediction


def predict_price(product_name: str) -> dict | None:
    """
    Predict the next price for a product using Linear Regression on
    its historical price data.

    Args:
        product_name: The product search term to look up history for.

    Returns:
        dict with keys:
            - predicted_price (float): Rounded predicted next price in INR.
            - trend (str): "UP", "DOWN", or "STABLE".
        None if insufficient history data exists.
    """
    logger.info("Running price prediction for: '%s'", product_name)

    try:
        rows = get_price_history(product_name)
    except Exception as exc:
        logger.error("Failed to fetch history for prediction: %s", exc)
        return None

    if not rows or len(rows) < MIN_DATA_POINTS:
        logger.warning(
            "Insufficient history for '%s': %d entry/entries (minimum %d).",
            product_name, len(rows) if rows else 0, MIN_DATA_POINTS
        )
        return None

    # Extract prices in chronological order
    prices = [row["price"] for row in rows]

    # Feature: time index (0, 1, 2, …, n)
    X = np.arange(len(prices)).reshape(-1, 1)
    y = np.array(prices)

    try:
        model = LinearRegression()
        model.fit(X, y)

        # Predict the NEXT time step
        next_index = np.array([[len(prices)]])
        predicted = float(model.predict(next_index)[0])
        predicted = max(0.0, round(predicted, 2))  # clip to non-negative
    except Exception as exc:
        logger.error("Linear Regression failed for '%s': %s", product_name, exc)
        return None

    # Determine trend via slope of the fitted line
    slope = float(model.coef_[0])
    trend_threshold = 0.5  # INR per time step

    if slope > trend_threshold:
        trend = "UP"
    elif slope < -trend_threshold:
        trend = "DOWN"
    else:
        trend = "STABLE"

    logger.info(
        "Prediction for '%s': ₹%.2f | slope=%.2f | trend=%s",
        product_name, predicted, slope, trend
    )

    return {
        "predicted_price": predicted,
        "trend": trend,
    }
