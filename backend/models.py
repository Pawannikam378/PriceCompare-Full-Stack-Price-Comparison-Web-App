"""
models.py
---------
Pydantic schemas used for request validation and API response serialization.
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class ProductResult(BaseModel):
    """A single product result returned from a marketplace."""
    platform: str = Field(..., description="Marketplace name (Amazon, Flipkart, Croma)")
    price: float = Field(..., ge=0, description="Current price in INR")
    rating: float = Field(..., ge=0, le=5, description="Customer rating out of 5")
    link: str = Field(..., description="Product page URL")
    is_cheapest: bool = Field(False, description="True if this is the cheapest option")

    class Config:
        json_schema_extra = {
            "example": {
                "platform": "Amazon",
                "price": 12999.0,
                "rating": 4.3,
                "link": "https://www.amazon.in/s?k=iphone",
                "is_cheapest": True,
            }
        }


class SearchResponse(BaseModel):
    """Full search response containing all platform results."""
    query: str
    results: list[ProductResult]
    cheapest: Optional[ProductResult] = None


class PriceHistoryEntry(BaseModel):
    """One data point in a product's price history."""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    price: float
    platform: Optional[str] = None


class HistoryResponse(BaseModel):
    """Full price history response."""
    product: str
    history: list[PriceHistoryEntry]
    lowest_price: Optional[float] = None
    highest_price: Optional[float] = None
