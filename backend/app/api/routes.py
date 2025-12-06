from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.card import Card as CardSchema, CardCreate
from app.db.database import get_db
from app.db.models import Card as CardModel

router = APIRouter()


@router.get("/cards", response_model=List[CardSchema])
async def get_cards(db: Session = Depends(get_db)):
    """Get all cards in the collection"""
    cards = db.query(CardModel).order_by(CardModel.created_at.desc()).all()
    return cards


@router.post("/cards", response_model=CardSchema)
async def create_card(card: CardCreate, db: Session = Depends(get_db)):
    """Manually add a card to the collection"""
    db_card = CardModel(**card.model_dump())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


@router.post("/cards/scan")
async def scan_card(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and scan a card image"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # TODO: Implement image processing and card recognition
    # For now, create a placeholder card
    db_card = CardModel(
        player_name="Unknown Player",
        notes=f"Scanned from file: {file.filename}"
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)

    return {
        "message": "Card scanned successfully",
        "filename": file.filename,
        "card_id": db_card.id
    }


@router.get("/cards/{card_id}", response_model=CardSchema)
async def get_card(card_id: int, db: Session = Depends(get_db)):
    """Get a specific card by ID"""
    card = db.query(CardModel).filter(CardModel.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.put("/cards/{card_id}", response_model=CardSchema)
async def update_card(card_id: int, card: CardCreate, db: Session = Depends(get_db)):
    """Update a card"""
    db_card = db.query(CardModel).filter(CardModel.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")

    for key, value in card.model_dump().items():
        setattr(db_card, key, value)

    db.commit()
    db.refresh(db_card)
    return db_card


@router.delete("/cards/{card_id}")
async def delete_card(card_id: int, db: Session = Depends(get_db)):
    """Delete a card"""
    db_card = db.query(CardModel).filter(CardModel.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")

    db.delete(db_card)
    db.commit()
    return {"message": "Card deleted successfully"}


@router.get("/cards/{card_id}/price")
async def get_card_price(card_id: int, db: Session = Depends(get_db)):
    """Get price information for a card using AI agents"""
    card = db.query(CardModel).filter(CardModel.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # TODO: Implement AI agent for price discovery
    return {
        "card_id": card_id,
        "player_name": card.player_name,
        "average_price": 0.0,
        "sources": []
    }
