from pydantic import BaseModel
from typing import Optional

class ItemCreate(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True  # Wichtig für die Konvertierung von SQLAlchemy-Objekten

class ItemResponse(ItemCreate):
    id: int

    class Config:
        orm_mode = True  # Ermöglicht FastAPI die Konvertierung von SQLAlchemy-Objekten