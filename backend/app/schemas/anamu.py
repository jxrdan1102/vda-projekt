from datetime import datetime

from app.schemas.anakomp import Anakomp
from app.schemas.anakomp import AnakompForAnamuR
from app.schemas.anakonst import Anakonst
from app.schemas.anakonst import AnakonstForAnamuR
from app.schemas.modell import ModellForAnamuR
from app.schemas.modell import ModellIDResponse
from pydantic import BaseModel


class AnamuModellidOnly(BaseModel):
    fk_modell: int

    class Config:
        from_attributes = True

class AnamuBase(BaseModel):
    name: str
    fk_modell: int
    aenderungszustand: str
    identnr: int
    creation: datetime

    class Config:
        from_attributes = True

class AnamuGetR(AnamuBase):
    pass


class Anamu(AnamuBase):
    pass

class AnamuGetIdR(BaseModel):
    name: str
    aenderungszustand: str
    identnr: int | None = None
    modell: ModellForAnamuR
    anakomp: list[AnakompForAnamuR] | None = None
    anakonst: list[AnakonstForAnamuR] | None = None

    class Config:
        from_attributes = True

class AnamuIdGet(BaseModel):
    name: str
    aenderungszustand: str
    identnr: int
    modell: ModellIDResponse

    class Config:
        from_attributes = True

class AnamuCreate(AnamuBase):
    partno: int
    remark: int
    modify: datetime
    user: int
    tolfaktor: int
    tsk_aufgabe: int
    fk_kmg: int
    anakomps: list[Anakomp] = []
    anakonst: list[Anakonst] = []

    class Config:
        from_attributes = True

class AnamuCreateR(BaseModel):
    name: str
    fk_modell: int
    aenderungszustand: str

    class Config:
        from_attributes = True