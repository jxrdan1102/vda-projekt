# schemas/kmg.py

from pydantic import BaseModel


class KMGBase(BaseModel):
    kmg_ident: str | None = None
    kmg_bez: str | None = None
    kmg_a: float | None = None
    kmg_k: float | None = None
    kmg_lt: float | None = None
    kmg_uc: float | None = None
    kmg_alpham: float | None = None
    kmg_mpeml: float | None = None


class KMGCreate(KMGBase):
    pass


class KMGUpdate(BaseModel):
    kmg_bez: str | None = None
    kmg_a: float | None = None
    kmg_k: float | None = None
    kmg_lt: float | None = None
    kmg_uc: float | None = None
    kmg_alpham: float | None = None
    kmg_mpeml: float | None = None


class KMGResponse(KMGBase):
    id: int
    kmg_bez: str

    class Config:
        from_attributes = True
