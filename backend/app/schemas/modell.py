from datetime import datetime
from typing import List, Optional, Set

from pydantic import BaseModel, Field

from app.schemas.component import ComponentGet, ComponentGetModell, ComponentRefCreate
from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TKompConstants,
    TMU_ConstList,
)


class ModellBase(BaseModel):
    id: int
    aufgabe: int


class ModellCreate(BaseModel):
    name: str
    description: Optional[str] = None
    geo_me: Optional[int] = None
    geo_mo: Optional[int] = None
    geo_gn: int
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

    components: Optional[List[ComponentRefCreate]] = (
        None  # Beziehung zur Component-Klasse
    )

    class Config:
        orm_mode = True


class ModellUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    geo_me: Optional[int] = None
    geo_mo: Optional[int] = None
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

    components: Optional[List[ComponentRefCreate]] = (
        None  # Beziehung zur Component-Klasse
    )

    class Config:
        orm_mode = True


class ModellNameDescription(BaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True
        from_attributes = True


class ModellIDResponse(BaseModel):
    name: str
    description: Optional[str]
    components: Optional[List[ComponentGetModell]] = None
    constantsValue: Optional[TMU_ConstList] = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        json_encoders = {TKompConstants: lambda v: v.name}
