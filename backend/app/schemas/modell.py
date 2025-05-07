from datetime import datetime
from typing import List

from app.schemas.component import ComponentGetModell, ComponentRefCreate
from app.schemas.component import ComponentGetR
from app.schemas.component import TMU_Komponente_Pydantic
from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TKompConstants,
    TMU_ConstList,
)
from pydantic import BaseModel


class ModellGetAllR(BaseModel):
    name: str
    description: str | None = None

    class Config:
        orm_mode = True

class ModellBase(BaseModel):
    id: int
    aufgabe: int

    class Config:
        orm_mode = True

class ModellCreateR(BaseModel):
    iGeometrie_EN: int # Prozess
    name: str
    aufgabe: int | None = None

    class Config:
        orm_mode = True

class ModellForAnamuR(BaseModel):
    name: str
    aufgabe: int
    methode: int
    geo_me: int
    geo_mo: int

    class Config:
        orm_mode = True

class ModellUpdateR(BaseModel):
    name: str | None = None
    geo_me: int | None = None # Messeinrichtung
    geo_mo: int | None = None # Messobjekt
    geo_bn: int | None = None # Einstellnormal
    methode: int | None = None # Methode
    tsk_ausenmessung: int | None = None
    tsk_innenmessung: int | None = None
    tsk_tiefenmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None
    formel: str | None = None
    formeldesc: str | None = None

    class Config:
        orm_mode = True

class ModellGetIdR(BaseModel):
    name: str | None = None
    geo_me: int | None = None # Messeinrichtung
    geo_mo: int | None = None # Messobjekt
    geo_bn: int | None = None # Einstellnormal
    methode: int | None = None # Methode
    tsk_ausenmessung: int | None = None
    tsk_innenmessung: int | None = None
    tsk_tiefenmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None
    formel: str | None = None
    formeldesc: str | None = None

    components: list[ComponentGetR] | None = None

    class Config:
        orm_mode = True

class ModellCreate(BaseModel):
    name: str
    description: str | None = None
    geo_me: int | None = None
    geo_mo: int | None = None
    iGeometrie_EN: int
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


class ModellNameDescription(ModellBase):
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


class TMU_Modell_Pydantic(BaseModel):
    aufgabe: int
    modell_id: int

    components: List[TMU_Komponente_Pydantic]

    class Config:
        orm_mode = True  # Erlaubt die Konvertierung von ORM-Modellen in Pydantic-Modelle