from typing import Optional

from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True
