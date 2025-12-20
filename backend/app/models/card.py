from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CardBase(BaseModel):
    player_name: str
    year: Optional[int] = None
    brand: Optional[str] = None
    card_number: Optional[str] = None
    set_name: Optional[str] = None
    sport: Optional[str] = None
    condition: Optional[str] = None
    notes: Optional[str] = None


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CardScanResponse(BaseModel):
    """Response schema for card scanning endpoint"""
    message: str
    card_id: int
    image_url: str
    card: Card
    metadata_extracted: bool
    extraction_confidence: Optional[str] = None

    class Config:
        from_attributes = True


class CardPrice(BaseModel):
    card_id: int
    average_price: float
    low_price: Optional[float] = None
    high_price: Optional[float] = None
    last_updated: datetime
    sources: list[str] = []
