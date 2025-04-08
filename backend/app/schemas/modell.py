from datetime import datetime
from typing import Optional, List, Set

from pydantic import BaseModel

from app.schemas.component import ComponentRefCreate


class ModellCreate(BaseModel):
    name: str
    description: Optional[str] = None
    geo_me: Optional[int] = None
    geo_mo: Optional[int] = None
    geo_gn: Optional[int] = None
    geo_bn: Optional[int] = None
    tol_fak: Optional[int] = None
    aufgabe: Optional[int] = None
    methode: Optional[int] = None
    gegenstanf: Optional[int] = None
    messeinsatz: Optional[int] = None
    einstellmass: Optional[int] = None
    modcreation: Optional[datetime] = None
    modmod: Optional[datetime] = None
    tsk_ausenmessung: Optional[int] = None
    tsk_innenmessung: Optional[int] = None
    tsk_tiefenmessung: Optional[int] = None
    tsk_hoehenmessung: Optional[int] = None
    tsk_stufenmessung: Optional[int] = None
    formel: Optional[str] = None
    formeldesc: Optional[str] = None

    components: List[ComponentRefCreate] = []  # Beziehung zur Component-Klasse

    class Config:
        orm_mode = True


class ModellNameDescription(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True

class ModellIDResponse(BaseModel):
    name: str
    description: Optional[str]
    constants: Set[str]