from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.schemas.component import ComponentGetModell, ComponentRefCreate
from app.schemas.component import ComponentGetR
from app.schemas.component import TMU_Komponente_Pydantic
from app.services.component_service.EverythinForComponents.TMU_ConstList import (
    TKompConstants,
    TMU_ConstList,
)


class DuplicateRequest(BaseModel):
    name: str

class ModellGetAllR(BaseModel):
    id: int
    name: str
    description: str | None = None
    aufgabe_modell: int | None = None
    aufgabe: int | None = None
    methode: int | None = None
    geo_me: int | None = None
    geo_mo: int | None = None
    tsk_innenmessung: int | None = None
    tsk_ausenmessung: int | None = None
    tsk_tiefennmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None

    class Config:
        from_attributes = True

class ModellBase(BaseModel):
    id: int
    aufgabe: int
    is_builtin: bool

    class Config:
        from_attributes = True

class ModellCreateR(BaseModel):
    aufgabe_modell: int # Prozess
    name: str
    aufgabe: int | None = None
    gegenstand: int | None = 0
    einstellmass: int | None = 0
    methode: int | None = 0

    class Config:
        from_attributes = True

class ModellForAnamuR(BaseModel):
    id: int
    name: str
    aufgabe: int | None = None
    methode: int | None = None
    aufgabe_modell: int | None = None
    geo_me: int | None = None
    geo_mo: int | None = None
    tsk_innenmessung: int | None = None
    tsk_ausenmessung: int | None = None
    tsk_tiefenmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None
    modcreation: str | None = None

    class Config:
        from_attributes = True

class ModellUpdateR(BaseModel):
    name: str | None = None
    aufgabe_modell: int
    aufgabe: int | None = None
    geo_me: int | None = None # Messeinrichtung
    geo_mo: int | None = None # Messobjekt
    geo_bn: int | None = None # Einstellnormal
    methode: int | None = None # Methode
    tsk_ausenmessung: int | None = None
    tsk_innenmessung: int | None = None
    tsk_tiefenmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None
    Bezug1: str | None = None
    Bezug2: str | None = None
    winkelE1: int | None = None
    winkelE2: int | None = None
    Element1: str | None = None
    Element2: str | None = None
    punktmuster: int | None = None
    taster: int | None = None
    merkmal: int | None = None
    element: int | None = None
    punktmusterB1: int | None = None
    tasterschaft1: int | None = None
    tasterschaft2: int | None = None
    artdesmasses: int | None = None
    punktmusterR1: int | None = None
    punktmusterR2: int | None = None
    taster1: int | None = None
    taster2: int | None = None
    abstand: int | None = None
    description: str | None = None
    formel: str | None = None
    formeldesc: str | None = None
    is_builtin: int | None = None
    class Config:
        from_attributes = True

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
    gegenstand: int | None = None
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
        from_attributes = True

class ModellUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    geo_me: int | None = None
    geo_mo: int | None = None
    geo_bn: int | None = None
    tol_fak: int | None = None
    aufgabe: int | None = None
    methode: int | None = None
    gegenstand: int | None = None
    messeinsatz: int | None = None
    einstellmass: int | None = None
    modcreation: datetime | None = None
    modmod: datetime | None = None
    tsk_ausenmessung: int | None = None
    tsk_innenmessung: int | None = None
    tsk_tiefenmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None
    taster: int | None = None
    merkmal: int | None = None
    element: int | None = None
    punktmusterB1: int | None = None
    tasterschaft1: int | None = None
    tasterschaft2: int | None = None
    punktmusterR1: int | None = None
    punktmusterR2: int | None = None
    taster1: int | None = None
    taster2: int | None = None
    abstand: int | None = None
    Bezug1: str | None = None
    Bezug2: str | None = None
    Element1: str | None = None
    Element2: str | None = None
    punktmuster: int | None = None
    formel: str | None = None
    formeldesc: str | None = None
    aufgabe_modell: int

    components: list[ComponentRefCreate] | None = None  # Beziehung zur Component-Klasse

    class Config:
        from_attributes = True

class ModellAlter(ModellUpdateR):
    aufgabe: int | None = None

class ModellNameDescription(ModellBase):
    name: str
    description: str

    class Config:
        from_attributes = True


class ModellIDResponse(BaseModel):
    name: str
    description: str | None
    components: list[ComponentGetModell] | None = None
    constantsValue: TMU_ConstList | None = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {TKompConstants: lambda v: v.name}


class ModellGetIdR(BaseModel):
    name: str | None = None
    geo_me: int | None = None # Messeinrichtung
    geo_mo: int | None = None # Messobjekt
    geo_bn: int | None = None # Einstellnormal
    methode: int | None = None # Methode
    aufgabe: int | None = None
    tsk_ausenmessung: int | None = None
    tsk_innenmessung: int | None = None
    tsk_tiefenmessung: int | None = None
    tsk_hoehenmessung: int | None = None
    tsk_stufenmessung: int | None = None
    taster: int | None = None
    merkmal: int | None = None
    element: int | None = None
    winkelE1 : int | None = None
    winkelE2 : int | None = None
    punktmusterB1: int | None = None
    tasterschaft1: int | None = None
    tasterschaft2: int | None = None
    artdesmasses: int | None = None
    punktmusterR1: int | None = None
    punktmusterR2: int | None = None
    taster1: int | None = None
    taster2: int | None = None
    abstand: int | None = None

    Bezug1: str | None = None
    Bezug2: str | None = None
    Element1: str | None = None
    Element2: str | None = None
    punktmuster: int | None = None
    description: str | None = None
    formel: str | None = None
    formeldesc: str | None = None
    aufgabe_modell: int
    is_builtin: int

    components: list[ComponentGetR] | None = None

    class Config:
        from_attributes = True


class TMU_Modell_Pydantic(BaseModel):
    aufgabe: int
    modell_id: int

    components: List[TMU_Komponente_Pydantic]

    class Config:
        from_attributes = True  # Erlaubt die Konvertierung von ORM-Modellen in Pydantic-Modelle