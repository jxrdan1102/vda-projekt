from typing import Optional
from pydantic import BaseModel

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


class TMuKompRec(BaseModel):
    terml0: float
    terml1: float
    verteilung: int
    kennwertart: int
    freiheitsgrad: int
    frei_n_minus_1: int
    flags: int

    class Config:
        arbitrary_types_allowed = True


class ComponentBack(BaseModel):
    TermL0: float
    TermL1: float
    Verteilung: str
    KennwertArt: str
    Freiheitsgrad: str
    FreiN_minus_1: int
    Flags: int
