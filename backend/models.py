from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    original_image_path = Column(String)
    card_image_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)

    fields = relationship("ScanField", back_populates="scan", cascade="all, delete-orphan")

class ScanField(Base):
    __tablename__ = "scan_fields"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    text = Column(String)
    confidence = Column(Float, default=0.0)
    x = Column(Integer)
    y = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    image_path = Column(String)

    scan = relationship("Scan", back_populates="fields")
