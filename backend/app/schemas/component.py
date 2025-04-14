from typing import Optional, List, Set
from pydantic import BaseModel

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants

from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec

from app.services.component_service.EverythinForComponents.TMuKompRec import TMU_Verteilung, TMU_Freiheitsgrad, \
    TMU_KennwertArt


class ComponentRefBase(BaseModel):
    lfdnr: Optional[int] = None
    kompid: Optional[int] = None
    modltxtid: Optional[int] = None
    terml0: Optional[float] = None
    terml1: Optional[float] = None
    wertart: Optional[int] = None
    freigrad: Optional[int] = None
    frei_n_1: Optional[int] = None
    verteilung: Optional[int] = None
    kflags: Optional[int] = None

    class Config:
        orm_mode = True

class ComponentGet(ComponentRefBase):
    pass

class ComponentRefCreate(ComponentRefBase):
    pass

class ComponentRefUpdate(ComponentRefBase):
    pass

class ComponentBack(BaseModel):
    ConstNeeded: Set[str]
    data: dict

    class Config:
        json_encoders = {
            str: lambda v: v.upper()
        }
class ComponentKompidOnly(BaseModel):
    kompid: int

class ComponentData(BaseModel):
    terml0: Optional[float] = None
    terml1: Optional[float] = None
    verteilung: Optional[int] = None
    wertart: Optional[int] = None
    freigrad: Optional[int] = None
    frei_n_1: Optional[int] = None
