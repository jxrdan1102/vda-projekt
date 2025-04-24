# schemas/kmg.py
from typing import Optional

from pydantic import BaseModel


class KMGBase(BaseModel):
    kmg_ident: int
    kmg_bez: str
    kmg_a: float
    kmg_k: float
    kmg_lt: float
    kmg_uc: float
    kmg_alpham: float
    kmg_mpeml: float


class KMGCreate(KMGBase):
    pass


class KMGUpdate(BaseModel):
    kmg_bez: Optional[str]
    kmg_a: Optional[float]
    kmg_k: Optional[float]
    kmg_lt: Optional[float]
    kmg_uc: Optional[float]
    kmg_alpham: Optional[float]
    kmg_mpeml: Optional[float]


class KMGResponse(KMGBase):
    id: int

    class Config:
        orm_mode = True