"""
Service for researching card prices via eBay Browse API
"""
import base64
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import httpx
from app.core.config import settings
from app.models.card import CardPrice

logger = logging.getLogger(__name__)

EBAY_AUTH_URL = "https://api.ebay.com/identity/v1/oauth2/token"
EBAY_BROWSE_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"
EBAY_SCOPE = "https://api.ebay.com/oauth/api_scope"


class PriceService:
    """Service for researching card prices via eBay Browse API"""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or settings.EBAY_CLIENT_ID
        self.client_secret = client_secret or settings.EBAY_CLIENT_SECRET
        self._access_token: Optional[str] = None

        if not self.client_id or not self.client_secret:
            logger.warning("eBay API credentials not configured - price service unavailable")

    def is_available(self) -> bool:
        """Check if price service is available (API credentials configured)"""
        return bool(self.client_id and self.client_secret)

    async def _get_access_token(self) -> str:
        """Get OAuth access token using client credentials grant."""
        if self._access_token:
            return self._access_token

        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                EBAY_AUTH_URL,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": EBAY_SCOPE,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            self._access_token = data["access_token"]
            return self._access_token

    async def get_card_price(self, card) -> CardPrice:
        """
        Get price information for a card by searching eBay listings.

        Args:
            card: Card database model with metadata fields

        Returns:
            CardPrice with average, low, high prices and sources
        """
        if not self.is_available():
            logger.info("Price service not available - returning empty price")
            return self._empty_price(card.id)

        try:
            query = self._build_search_query(card)
            logger.info(f"Searching eBay for card {card.id}: {query}")

            listings = await self._search_ebay(query)
            return self._calculate_average_price(card.id, listings)

        except Exception as e:
            logger.exception(f"Error getting price for card {card.id}: {str(e)}")
            return self._empty_price(card.id)

    async def _search_ebay(self, query: str) -> List[Dict]:
        """
        Search eBay Browse API for listings matching the query.

        Returns:
            List of dicts with keys: title, price, currency
        """
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                EBAY_BROWSE_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                },
                params={
                    "q": query,
                    "category_ids": "261328",  # Sports Trading Cards
                    "filter": "buyingOptions:{FIXED_PRICE},conditions:{NEW|LIKE_NEW|VERY_GOOD}",
                    "sort": "price",
                    "limit": "25",
                },
                timeout=15,
            )

            if response.status_code == 401:
                # Token expired, clear and retry once
                self._access_token = None
                token = await self._get_access_token()
                response = await client.get(
                    EBAY_BROWSE_URL,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
                    },
                    params={
                        "q": query,
                        "category_ids": "261328",
                        "filter": "buyingOptions:{FIXED_PRICE},conditions:{NEW|LIKE_NEW|VERY_GOOD}",
                        "sort": "price",
                        "limit": "25",
                    },
                    timeout=15,
                )

            response.raise_for_status()
            data = response.json()

        items = data.get("itemSummaries", [])
        if not items:
            logger.info(f"No eBay results for query: {query}")
            return []

        listings = []
        for item in items:
            price_info = item.get("price", {})
            try:
                price = float(price_info.get("value", 0))
                if price > 0:
                    listings.append({
                        "title": item.get("title", ""),
                        "price": price,
                        "currency": price_info.get("currency", "USD"),
                    })
            except (ValueError, TypeError):
                continue

        logger.info(f"Found {len(listings)} eBay listings with prices")
        return listings

    def _build_search_query(self, card) -> str:
        """Build an eBay search query string from card metadata."""
        parts = [card.player_name]
        if card.year:
            parts.append(str(card.year))
        if card.brand:
            parts.append(card.brand)
        if card.set_name:
            parts.append(card.set_name)
        if card.card_number:
            parts.append(f"#{card.card_number}")
        if card.sport:
            parts.append(card.sport)
        parts.append("card")
        return " ".join(parts)

    def _calculate_average_price(self, card_id: int, listings: List[Dict]) -> CardPrice:
        """Calculate price statistics from listing data."""
        if not listings:
            return self._empty_price(card_id)

        prices = [listing["price"] for listing in listings]

        # Remove outliers: drop prices outside 1.5x IQR if we have enough data
        if len(prices) >= 5:
            prices.sort()
            q1 = prices[len(prices) // 4]
            q3 = prices[3 * len(prices) // 4]
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            filtered = [p for p in prices if lower <= p <= upper]
            if filtered:
                prices = filtered

        return CardPrice(
            card_id=card_id,
            average_price=round(sum(prices) / len(prices), 2),
            low_price=min(prices),
            high_price=max(prices),
            last_updated=datetime.now(timezone.utc),
            sources=["ebay"]
        )

    def _empty_price(self, card_id: int) -> CardPrice:
        """Return a zeroed-out CardPrice when no data is available."""
        return CardPrice(
            card_id=card_id,
            average_price=0.0,
            last_updated=datetime.now(timezone.utc),
            sources=[]
        )
