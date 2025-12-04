from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from app.models.card import Card, CardCreate

router = APIRouter()


@router.get("/cards", response_model=List[Card])
async def get_cards():
    """Get all cards in the collection"""
    # TODO: Implement database query
    return []


@router.post("/cards", response_model=Card)
async def create_card(card: CardCreate):
    """Manually add a card to the collection"""
    # TODO: Implement card creation
    return card


@router.post("/cards/scan")
async def scan_card(file: UploadFile = File(...)):
    """Upload and scan a card image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # TODO: Implement image processing and card recognition
    return {
        "message": "Card scanned successfully",
        "filename": file.filename
    }


@router.get("/cards/{card_id}", response_model=Card)
async def get_card(card_id: int):
    """Get a specific card by ID"""
    # TODO: Implement database query
    raise HTTPException(status_code=404, detail="Card not found")


@router.get("/cards/{card_id}/price")
async def get_card_price(card_id: int):
    """Get price information for a card using AI agents"""
    # TODO: Implement AI agent for price discovery
    return {
        "card_id": card_id,
        "average_price": 0.0,
        "sources": []
    }
