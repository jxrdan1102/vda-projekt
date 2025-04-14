from typing import Optional

from pydantic import BaseModel

class AnakompBase(BaseModel):
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

class Anakomp(AnakompBase):
    pass

class AnakompUpdate(AnakompBase):
    pass