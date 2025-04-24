from typing import List, Optional, Set

from pydantic import BaseModel

from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TKompConstants,
)
from app.services.component_service.EverythinForComponents.TMuKompRec import (
    TMU_Freiheitsgrad,
    TMU_KennwertArt,
    TMU_Verteilung,
    TMuKompRec,
)


class ComponentGetModell(BaseModel):
    id: int
    kompid: int
    modltxtid: Optional[int] = None

    class Config:
        orm_mode = True


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
    data: TMuKompRec
    ConstNeeded: Set[str]

    class Config:
        json_encoders = {str: lambda v: v.upper()}


class ComponentKompidOnly(BaseModel):
    kompid: int


class ComponentData(BaseModel):
    terml0: Optional[float] = None
    terml1: Optional[float] = None
    verteilung: Optional[int] = None
    wertart: Optional[int] = None
    freigrad: Optional[int] = None
    frei_n_1: Optional[int] = None
