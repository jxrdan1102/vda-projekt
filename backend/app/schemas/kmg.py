# schemas/kmg.py

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
    kmg_bez: str | None
    kmg_a: float | None
    kmg_k: float | None
    kmg_lt: float | None
    kmg_uc: float | None
    kmg_alpham: float | None
    kmg_mpeml: float | None


class KMGResponse(KMGBase):
    id: int

    class Config:
        orm_mode = True
