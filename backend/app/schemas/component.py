from typing import Optional, List, Set
from pydantic import BaseModel

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants

from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec

from app.services.component_service.EverythinForComponents.TMuKompRec import TMU_Verteilung, TMU_Freiheitsgrad, \
    TMU_KennwertArt


class ComponentRefCreate(BaseModel):
    #fk_modell: int muss glaub ich in Logik direkt nach Create von Modell übergeben werden
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

class ComponentRefUpdate(BaseModel):
    lfdnr: Optional[int] = None
    kompid: int
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



class ComponentBack(BaseModel):
    ConstNeeded: Set[TKompConstants]
    data: TMuKompRec

    class Config:
        json_encoders = {
            TKompConstants: lambda v: v.name,
        }