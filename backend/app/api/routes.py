from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pathlib import Path
import logging
from app.models.card import Card as CardSchema, CardCreate, CardScanResponse
from app.db.database import get_db
from app.db.models import Card as CardModel
from app.services.image_service import ImageService
from app.services.vision_service import VisionService
from app.core.config import settings

logger = logging.getLogger(__name__)

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


@router.post("/cards/scan", response_model=CardScanResponse)
async def scan_card(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload and scan a card image with automatic metadata extraction"""
    # Validate content type early
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Create placeholder card first (to get ID for storage path)
    db_card = CardModel(
        player_name="Unknown Player",
        notes=f"Scanned from file: {file.filename}"
    )
    db.add(db_card)
    db.commit()
    db.refresh(db_card)

    try:
        # Process and save image
        image_service = ImageService()
        image_url = await image_service.save_card_image(file, db_card.id)

        # Update card with image URL
        db_card.image_url = image_url
        db.commit()

        # Extract metadata using Vision API
        metadata_extracted = False
        extraction_confidence = None
        extraction_error = None

        vision_service = VisionService()
        if settings.ENABLE_VISION_EXTRACTION and vision_service.is_available():
            # Convert image_url to absolute file path
            # image_url format: /uploads/{card_id}/{filename}
            relative_path = image_url.lstrip('/uploads/')
            image_path = Path(settings.UPLOAD_DIR) / relative_path

            metadata, confidence, error = await vision_service.extract_card_metadata(
                str(image_path)
            )

            if metadata:
                # Update card with extracted metadata (only non-null values)
                for key, value in metadata.items():
                    if value is not None and hasattr(db_card, key):
                        setattr(db_card, key, value)

                db.commit()
                metadata_extracted = True
                extraction_confidence = confidence
            else:
                extraction_error = error
                logger.warning(
                    f"Vision API failed for card {db_card.id}: {error}"
                )
        else:
            if not settings.ENABLE_VISION_EXTRACTION:
                logger.info("Vision extraction disabled via feature flag")
            else:
                logger.info("Vision service not available - skipping metadata extraction")

        # Refresh to get updated values
        db.refresh(db_card)

        return {
            "message": "Card scanned successfully",
            "card_id": db_card.id,
            "image_url": image_url,
            "card": CardSchema.from_orm(db_card),
            "metadata_extracted": metadata_extracted,
            "extraction_confidence": extraction_confidence
        }

    except HTTPException:
        # Clean up card if image processing fails
        db.delete(db_card)
        db.commit()
        raise
    except Exception as e:
        # Clean up card and raise generic error
        logger.exception(f"Error processing card scan: {str(e)}")
        db.delete(db_card)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )


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

    # Delete associated image if exists
    if db_card.image_url:
        image_service = ImageService()
        await image_service.delete_card_image(db_card.image_url)

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
