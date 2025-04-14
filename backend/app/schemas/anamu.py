from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.anakomp import AnakompUpdate, Anakomp
from app.schemas.anakonst import Anakonst

class AnamuModellidOnly(BaseModel):
    fk_modell: int

class AnamuBase(BaseModel):
    name: str
    aenderungszustand: str
    identnr: int
    creation: datetime

    class Config:
        orm_mode = True

class Anamu(AnamuBase):
    pass

class AnamuCreate(AnamuBase):
    partno: int
    remark: int
    modify: datetime
    user: int
    tolfaktor: int
    tsk_aufgabe: int
    kmg_ident: str
    anakomps: List[Anakomp] = []
    anakonst: List[Anakonst] = []


