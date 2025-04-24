from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.anakomp import Anakomp, AnakompUpdate
from app.schemas.anakonst import Anakonst
from app.schemas.modell import ModellIDResponse


class AnamuModellidOnly(BaseModel):
    fk_modell: int


class AnamuBase(BaseModel):
    name: str
    fk_modell: int
    aenderungszustand: str
    identnr: int
    creation: datetime

    class Config:
        orm_mode = True


class Anamu(AnamuBase):
    pass


class AnamuIdGet(BaseModel):
    name: str
    aenderungszustand: str
    identnr: int
    modell: ModellIDResponse


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
