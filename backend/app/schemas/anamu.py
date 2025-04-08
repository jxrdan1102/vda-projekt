from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.anakomp import AnakompUpdate, Anakomp
from app.schemas.anakonst import Anakonst


class Anamu(BaseModel):
    name: str
    aenderungszustand: str
    fk_modell : int
    identnr : int
    #sachnummer : int
    creation : datetime

    class Config:
        orm_mode = True

class AnamuCreate(BaseModel):
    fk_modell: int
    name: str
    aenderungszustand: str
    identnr: int
    partno: int
    remark: int
    creation: datetime
    modify: datetime
    user: int
    tolfaktor: int
    tsk_aufgabe: int
    kmg_ident: str
    anakomps: List[Anakomp] = []  # Beziehung zur Component-Klasse
    anakonst: List[Anakonst] = []  # Beziehung zur Component-Klasse

    class Config:
        orm_mode = True


