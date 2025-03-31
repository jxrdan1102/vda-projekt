from typing import Optional
from pydantic import BaseModel


class Komponente(BaseModel):
    name: str
    a: int
    b: int
    c: int
    d: Optional[int] = None
    e: Optional[int] = None

    class Config:
        orm_mode = True
