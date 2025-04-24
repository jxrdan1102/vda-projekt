from datetime import datetime

from pydantic import BaseModel

from app.schemas.component import ComponentGetModell, ComponentRefCreate
from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TKompConstants,
    TMU_ConstList,
)


class ModellBase(BaseModel):
    id: int
    aufgabe: int


class ModellCreate(BaseModel):
    name: str
    description: str | None = None
    geo_me: int | None = None
    geo_mo: int | None = None
    geo_gn: int
    geo_bn: int | None = None
    tol_fak: int | None = None
    aufgabe: int | None = None
    methode: int | None = None
    gegenstanf: int | None = None
    messeinsatz: int | None = None
    einstellmass: int | None = None
    modcreation: datetime | None = None
    modmod: datetime | None = None
    tsk_ausenmessung: int | None = None
    tsk_innenmessung: int | None = None
    tsk_tiefenmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None
    formel: str | None = None
    formeldesc: str | None = None

    components: list[ComponentRefCreate] | None = None  # Beziehung zur Component-Klasse

    class Config:
        orm_mode = True


class ModellUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    geo_me: int | None = None
    geo_mo: int | None = None
    geo_bn: int | None = None
    tol_fak: int | None = None
    aufgabe: int | None = None
    methode: int | None = None
    gegenstanf: int | None = None
    messeinsatz: int | None = None
    einstellmass: int | None = None
    modcreation: datetime | None = None
    modmod: datetime | None = None
    tsk_ausenmessung: int | None = None
    tsk_innenmessung: int | None = None
    tsk_tiefenmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None
    formel: str | None = None
    formeldesc: str | None = None

    components: list[ComponentRefCreate] | None = None  # Beziehung zur Component-Klasse

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
    description: str | None
    components: list[ComponentGetModell] | None = None
    constantsValue: TMU_ConstList | None = None

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
        json_encoders = {TKompConstants: lambda v: v.name}
