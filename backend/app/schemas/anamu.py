from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.schemas.anakomp import Anakomp
from app.schemas.anakomp import AnakompForAnamuR
from app.schemas.anakonst import Anakonst
from app.schemas.anakonst import AnakonstForAnamuR
from app.schemas.kmg import KMGBase
from app.schemas.modell import ModellForAnamuR
from app.schemas.modell import ModellIDResponse


class AnamuModellidOnly(BaseModel):
    fk_modell: int

    class Config:
        from_attributes = True

class AnamuBase(BaseModel):
    id: int
    name: str
    fk_modell: int
    aenderungszustand: str
    identnr: int | None = None
    creation: datetime | None = None

    class Config:
        from_attributes = True

class AnamuGetR(AnamuBase):
    modell: ModellForAnamuR
    creation: datetime | None

    pass


class Anamu(AnamuBase):
    pass

class AnamuGetIdR(BaseModel):
    id: int
    name: str
    aenderungszustand: str
    identnr: int | None = None
    remark: str | None = None
    modell: ModellForAnamuR
    anakomp: list[AnakompForAnamuR] | None = None
    anakonst: list[AnakonstForAnamuR] | None = None
    fk_kmg: int | None = None
    tolfaktor: int | None = None
    kmg: Optional[KMGBase] | None = None
    class Config:
        from_attributes = True

class AnamuIdGet(BaseModel):
    name: str
    aenderungszustand: str
    identnr: int
    modell: ModellIDResponse
    fk_kmg: int | None = None
    tolfaktor:int | None = None
    class Config:
        from_attributes = True

class AnamuUpdate(BaseModel):
    name: str | None = None
    aenderungszustand: str | None = None
    identnr: int | None = None
    remark: str | None = None
    fk_kmg: int | None = None
    tolfaktor: int | None = None
    fk_modell: int | None = None
    class Config:
        from_attributes = True

class DuplicateAnamu(BaseModel):
    name: str

class AnamuOut(BaseModel):
    id: int
    name: str
    fk_modell: int
    aenderungszustand: str
    identnr: Optional[int] = None
    tolfaktor: int | None = None
    remark: Optional[str] = None
    creation: Optional[datetime] = None
    modell: ModellForAnamuR
    anakomp: Optional[List[AnakompForAnamuR]] = None
    anakonst: Optional[List[AnakonstForAnamuR]] = None

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