from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.db.database import Base


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String(255), nullable=False, index=True)
    year = Column(Integer, nullable=True)
    brand = Column(String(100), nullable=True)
    card_number = Column(String(50), nullable=True)
    set_name = Column(String(255), nullable=True)
    sport = Column(String(50), nullable=True, index=True)
    condition = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Card(id={self.id}, player_name='{self.player_name}', year={self.year})>"
