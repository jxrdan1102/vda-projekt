from typing import Optional

from pydantic import BaseModel

class Anakomp(BaseModel):
    fk_anamu: Optional[int] = None
    fk_mod_components: Optional[int] = None
    remark: Optional[str] = None
    terml0: Optional[float] = None
    terml1: Optional[float] = None
    wertart: Optional[int] = None
    freigrad: Optional[int] = None
    frei_n_1: Optional[int] = None
    verteilung: Optional[int] = None

    class Config:
        orm_mode = True

class AnakompUpdate(BaseModel):
    fk_anamu: Optional[int] = None
    fk_mod_components: Optional[int] = None
    remark: Optional[str] = None
    terml0: Optional[float] = None
    terml1: Optional[float] = None
    wertart: Optional[int] = None
    freigrad: Optional[int] = None
    frei_n_1: Optional[int] = None
    verteilung: Optional[int] = None

    class Config:
        orm_mode = True