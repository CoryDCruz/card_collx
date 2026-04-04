"""
Service for researching card prices via eBay sold listings
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from app.core.config import settings
from app.models.card import CardPrice

logger = logging.getLogger(__name__)


class PriceService:
    """Service for researching card prices via eBay sold listings"""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or settings.EBAY_CLIENT_ID
        self.client_secret = client_secret or settings.EBAY_CLIENT_SECRET
        if not self.client_id or not self.client_secret:
            logger.warning("eBay API credentials not configured - price service unavailable")
            self.client = None
        else:
            # TODO: Initialize eBay API client with OAuth token
            self.client = None
            logger.info("eBay price service initialized (client pending implementation)")

    def is_available(self) -> bool:
        """Check if price service is available (API credentials configured)"""
        return self.client is not None

    async def get_card_price(self, card) -> CardPrice:
        """
        Get price information for a card by searching eBay sold listings.

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
            logger.info(f"Searching eBay sold listings for card {card.id}: {query}")

            listings = await self.search_ebay_sold_listings(
                player_name=card.player_name,
                year=card.year,
                brand=card.brand,
                card_number=card.card_number,
                set_name=card.set_name,
                sport=card.sport
            )

            return self._calculate_average_price(card.id, listings)

        except Exception as e:
            logger.exception(f"Error getting price for card {card.id}: {str(e)}")
            return self._empty_price(card.id)

    async def search_ebay_sold_listings(
        self,
        player_name: str,
        year: Optional[int] = None,
        brand: Optional[str] = None,
        card_number: Optional[str] = None,
        set_name: Optional[str] = None,
        sport: Optional[str] = None
    ) -> List[Dict]:
        """
        Search eBay for completed/sold listings matching card metadata.

        Args:
            player_name: Player name to search for
            year: Card year
            brand: Card manufacturer
            card_number: Card number
            set_name: Set/series name
            sport: Sport type

        Returns:
            List of listing dicts with keys: title, price, date, url
        """
        # TODO: Implement with eBay Browse API
        # 1. Get OAuth token using client credentials
        # 2. Call /buy/browse/v1/item_summary/search with filters:
        #    - q: search query built from card metadata
        #    - filter: buyingOptions:{FIXED_PRICE|AUCTION}, conditionIds, price
        #    - sort: date (most recent sold)
        # 3. Parse response into standardized listing dicts
        logger.info(f"eBay search not yet implemented - query: {player_name} {year} {brand}")
        return []

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
        """Calculate price statistics from sold listing data."""
        if not listings:
            return self._empty_price(card_id)

        prices = [listing["price"] for listing in listings if "price" in listing]
        if not prices:
            return self._empty_price(card_id)

        return CardPrice(
            card_id=card_id,
            average_price=round(sum(prices) / len(prices), 2),
            low_price=min(prices),
            high_price=max(prices),
            last_updated=datetime.utcnow(),
            sources=["ebay_sold"]
        )

    def _empty_price(self, card_id: int) -> CardPrice:
        """Return a zeroed-out CardPrice when no data is available."""
        return CardPrice(
            card_id=card_id,
            average_price=0.0,
            last_updated=datetime.utcnow(),
            sources=[]
        )
