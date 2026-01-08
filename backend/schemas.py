from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ScanFieldBase(BaseModel):
    text: str
    confidence: Optional[float] = 0.0
    x: int
    y: int
    width: int
    height: int
    image_path: str

class ScanFieldCreate(ScanFieldBase):
    pass

class ScanField(ScanFieldBase):
    id: int
    scan_id: int

    class Config:
        orm_mode = True

class ScanBase(BaseModel):
    filename: str
    status: str
    original_image_path: str
    card_image_path: Optional[str] = None
    error_message: Optional[str] = None

class ScanCreate(ScanBase):
    pass

class Scan(ScanBase):
    id: int
    created_at: datetime
    fields: List[ScanField] = []

    class Config:
        orm_mode = True
