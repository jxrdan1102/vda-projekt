import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.component_service.EverythinForComponents.TMU_Atom import TMU_Atom
from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants, TMU_ConstList
from app.services.component_service.component_abstract import TMU_Komponente
from app.services.component_service.component_factory import ComponentFactory


# Definiere Enum für die zulässigen Prozess-Typen
class TMU_AufgabeModell(Enum):
    aPruefprozess = "aPruefprozess"
    aKalibrierprozess = "aKalibrierprozess"
    a3D_Pruefprozess = "a3D_Pruefprozess"
    aUnbekannt = "aUnbekannt"


# Konstanten
MU_NAN = float("nan")


# Hilfsfunktionen, um die Berechnungen zu ermöglichen
def power(value, exp):
    return value ** exp if not math.isnan(value) else MU_NAN

@dataclass
class TMU_Winkel:
    l: Optional[int] = None
    Winkel_Element1: Optional[int] = None
    Winkel_Element2: Optional[int] = None
    Winkel_Bezug1: Optional[int] = None
    Winkel_Bezug2: Optional[int] = None

    def is_l_variant(self):
        return self.l is not None

class TMU_Geometry(Enum):
    Geometrie_undefiniert = 0
    Flaeche = 1
    Kugel = 2
    Zylinder = 3
    HohlZylinder = 4  # Hohlzylinder wurde hinzugefügt


class TMU_3DElement(Enum):
    E3D_NDEF = "NDEF"
    E3D_Punkt = "Punkt"
    E3D_Gerade = "Gerade"
    E3D_Ebene = "Ebene"
    E3D_Kreis = "Kreis"
    E3D_Halbkugel = "Halbkugel"
    E3D_Zylinder = "Zylinder"
    E3D_Kegel = "Kegel"



class TMU_ModellSchema(BaseModel):
    aufgabe: int | None = None
    id: int
    mit_berechnung_toleranzfaktor: bool = False
    const_list: TMU_ConstList = Field(default_factory=TMU_ConstList)
    modell_name: str = ""
    AufgabeModell: TMU_AufgabeModell | None = None  # Kannst du nach Bedarf definieren
    i_aufgabe: int = 0
    i_geometrie_me: int = 0
    iGeometrie_EN: int | None = None
    i_geometrie_mo: int = 0
    read_only: bool = False
    modell_desc: str = ""
    methode: int = 0
    gegenstand: int = 0
    mess_einsatz: int = 0
    einstellmass: int = 0
    modell_created: datetime = datetime.now()
    modell_modified: datetime = datetime.now()
    punktmuster: int | None = None
    Element1: str | None = None
    Element2: str | None = None
    Bezug1: str | None = None
    Bezug2: str | None = None
    winkelE1: int | None = None
    winkelE2: int | None = None
    winkelB1: int | None = None
    winkelB2: int | None = None
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
    archiv: bool = False
    formel_anteil: str = ""
    formel_beschreibung: str = ""
    const_needed: set[TKompConstants] = set()  # Liste von TKompConstants

    @model_validator(mode="before")
    @classmethod
    def assign_geo_bn_to_igeometrie_en(cls, data):
        if hasattr(data, "geo_bn"):
            data.iGeometrie_EN = data.geo_bn
        if hasattr(data, "tsk_ausenmessung"):
            data.winkelE1 = data.tsk_ausenmessung
        if hasattr(data, "aufgabe_modell"):
            data.AufgabeModell = data.aufgabe_modell
        return data

    @field_validator("AufgabeModell", mode="before")
    @classmethod
    def convert_geometrie_enum(cls, value):
        # Mapping-Tabelle
        mapping = {
            1: TMU_AufgabeModell.aPruefprozess,
            2: TMU_AufgabeModell.aKalibrierprozess,
            3: TMU_AufgabeModell.a3D_Pruefprozess,
            0: TMU_AufgabeModell.aUnbekannt,
        }
        if isinstance(value, int):
            try:
                return mapping[value]
            except KeyError:
                raise ValueError(f"Invalid integer value for iGeometrie_EN: {value}")
        elif isinstance(value, str):
            return TMU_3DElement(value)
        return value


    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        from_attributes = True

class TMU_Modell(list[TMU_Komponente]):
    def __init__(self, schema: TMU_ModellSchema):
        super().__init__()
        self.iGeometrie_EN = schema.iGeometrie_EN
        self.Winkel = TMU_Winkel(Winkel_Bezug1=1,Winkel_Bezug2=1,Winkel_Element1=1,Winkel_Element2=1)
        self.Winkel.Winkel_Element1 = schema.winkelE1
        self.mit_berechnung_toleranzfaktor = schema.mit_berechnung_toleranzfaktor
        self.aufgabe = schema.aufgabe
        self.modell_name = schema.modell_name
        self.modell_id = schema.id
        self.AufgabeModell = schema.AufgabeModell
        self.i_aufgabe = schema.i_aufgabe
        self.i_geometrie_me = schema.i_geometrie_me
        self.i_geometrie_mo = schema.i_geometrie_mo
        self.read_only = schema.read_only
        self.modell_desc = schema.modell_desc
        self.methode = schema.methode
        self.gegenstand = schema.gegenstand
        self.mess_einsatz = schema.mess_einsatz
        self.einstellmass = schema.einstellmass
        self.modell_created = schema.modell_created
        self.modell_modified = schema.modell_modified
        self.archiv = schema.archiv
        self.formel_anteil = schema.formel_anteil
        self.formel_beschreibung = schema.formel_beschreibung
        self.const_needed = schema.const_needed
        self.const_list = schema.const_list
        self.buildConstList()
        self.punktmuster = schema.punktmuster
        self.Element1 = schema.Element1
        self.Element2 = schema.Element2
        self.Bezug1 = schema.Bezug1
        self.Bezug2 = schema.Bezug2
        self.winkelE1 = schema.winkelE1
        self.winkelE2 = schema.winkelE2
        self.winkelB1 = schema.winkelB1
        self.winkelB2 = schema.winkelB2
        self.taster = schema.taster
        self.merkmal = schema.merkmal
        self.element = schema.element
        self.punktmusterB1 = schema.punktmusterB1
        self.tasterschaft1 = schema.tasterschaft1
        self.tasterschaft2 = schema.tasterschaft2
        self.punktmusterR1 = schema.punktmusterR1
        self.punktmusterR2 = schema.punktmusterR2
        self.taster1 = schema.taster1
        self.taster2 = schema.taster2
        self.abstand = schema.abstand


    @classmethod
    def from_schema_params(cls, **kwargs):
        # Erstellt das Schema aus den gegebenen Parametern
        schema = TMU_ModellSchema(**kwargs)
        # Erstellt dann das Modell
        return cls(schema)

    async def setConstValue(self,anamu_id, db: AsyncSession):
        await self.const_list.load_constants(anamu_id,db)

    def addComponent(self, component_id: int,lfdnr):
        self.append(ComponentFactory.get_component(self, component_id,lfdnr))

    def SetBerechnungToleranzfaktor(self, ja: bool):
        self.mit_berechnung_toleranzfaktor = ja

    def Clear(self):
        self.Constlist.clear()
        self.iGeometrie_ME = 0  # Corresponds to ord(Flaeche)
        self.iGeometrie_MO = 0
        self.iGeometrie_EN = 0  # Corresponds to ord(Geometrie_undefiniert)
        self.Winkel["l"] = 0
        self.iBezug1 = 0
        self.iBezug2 = 0


    def buildConstList(self):

        if self.mit_berechnung_toleranzfaktor:
            self.const_needed.add(TKompConstants["TC_Nennmass"])
            self.const_needed.add(TKompConstants["TC_UntAbmass"])
            self.const_needed.add(TKompConstants["TC_ObAbmass"])
            self.const_list.const_map[TKompConstants["TC_Nennmass"]] = None
            self.const_list.const_map[TKompConstants["TC_UntAbmass"]] = None
            self.const_list.const_map[TKompConstants["TC_ObAbmass"]] = None

        if self.AufgabeModell.value == "a3D_Pruefprozess":
            self.const_needed.add(TKompConstants["TC_3d_KMG_A"])
            self.const_needed.add(TKompConstants["TC_3d_KMG_K"])
            self.const_needed.add(TKompConstants["TC_3d_KMG_Uc"])
            self.const_needed.add(TKompConstants["TC_3d_KMG_alphaM"])
            self.const_needed.add(TKompConstants["TC_3d_KMG_LT"])
            self.const_list.const_map[TKompConstants["TC_3d_KMG_A"]] = None
            self.const_list.const_map[TKompConstants["TC_3d_KMG_K"]] = None
            self.const_list.const_map[TKompConstants["TC_3d_KMG_Uc"]] = None
            self.const_list.const_map[TKompConstants["TC_3d_KMG_alphaM"]] = None
            self.const_list.const_map[TKompConstants["TC_3d_KMG_LT"]] = None

    def getConstTitle(self, cid):
        # Simulierter Funktionsaufruf zur Bestimmung des Titels
        return f"Title of {cid}"

    def FindKomp(self, ACompID):
        atom = None
        idx = 0
        while atom is None and idx < self.count:
            if isinstance(self[idx], TMU_Atom) and self[idx].id == ACompID:
                atom = self[idx]
            else:
                idx += 1
        return atom

    def Geometrie_ME(self):
        return TMU_Geometry(self.iGeometrie_ME + 1)

    def Geometrie_MO(self):
        return TMU_Geometry(self.iGeometrie_MO + 1)

    # def Geometrie_EN(self):
    #   return TMU_Geometry(self.iGeometrie_EN + 1)

    def Element1_3d(self):
        return TMU_3DElement(self.iGeometrie_EN)

    def Element2_3d(self):
        return TMU_3DElement(self.iGeometrie_MO)

    # def Bezug1_3d(self):
    #   return TMU_3DElement(self.iBezug1)

    def Bezug2_3d(self):
        return TMU_3DElement(self.iBezug2)

    @property
    def WinkelE1_3d(self):
        return self.Winkel.Winkel_Element1 + 1
    @property
    def WinkelE2_3d(self):
        return self.Winkel.Winkel_Element2 + 1
    @property
    def WinkelB1_3d(self):
        return self.Winkel.Winkel_Bezug1 + 1
    @property
    def WinkelB2_3d(self):
        return self.Winkel.Winkel_Bezug2 + 1

    def Merkmal_3d(self):
        return self.iGeometrie_ME

    def SummeDerVarianzen(self):
        v = 0
        valid = False
        for item in self:
            if isinstance(item, TMU_Komponente) and item.varianz() != MU_NAN:

                v += item.varianz()
                valid = True
        return v if valid else MU_NAN

    def StandardUnsicherheit_Uy(self):
        uy = self.SummeDerVarianzen()
        return math.sqrt(uy) if uy != MU_NAN else MU_NAN

    def V_eff(self):
        result = MU_NAN
        valid = False
        if self.AufgabeModell == "a3D_Pruefprozess":
            SummeEFG = 0
            U = self.StandardUnsicherheit_Uy()
            for item in self:
                if isinstance(item, TMU_Komponente):
                    vi = item.EffektiverFreiheitsgrad
                    if vi != MU_NAN:
                        SummeEFG += vi
            if (U + SummeEFG) == 0:
                result = 0
            elif power(U, 4) > (10000 * SummeEFG):
                result = 10000
            else:
                result = power(U, 4) / SummeEFG
        else:
            SummeUB = 0
            for item in self:
                if isinstance(item, TMU_Komponente):
                    ubi = item.unsicherheitsbeitrag
                    vi = item.effektiver_freiheitsgrad
                    if not math.isnan(ubi) and not math.isnan(vi):
                        SummeUB += power(ubi, 4) / vi
                        valid = True
            if valid:
                uy = self.StandardUnsicherheit_Uy()
                if uy != MU_NAN:
                    try:
                        if SummeUB == 0:
                            result = 500
                        else:
                            result = power(uy, 4) / SummeUB
                    except BaseException:
                        result = MU_NAN
        return result

    def Erweiterungsfaktor_k(self):
        veff = self.V_eff()
        if not math.isnan(veff):
            if self.AufgabeModell == "a3D_Pruefprozess":
                result = 2.0
            else:
                if veff >= 500:
                    result = 2.00
                elif veff >= 100:
                    result = 2.02
                elif veff >= 50:
                    result = 2.05
                elif veff >= 45:
                    result = 2.06
                elif veff >= 40:
                    result = 2.06
                elif veff >= 35:
                    result = 2.07
                elif veff >= 30:
                    result = 2.09
                elif veff >= 25:
                    result = 2.11
                elif veff >= 20:
                    result = 2.13
                elif veff >= 19:
                    result = 2.14
                elif veff >= 18:
                    result = 2.15
                elif veff >= 17:
                    result = 2.16
                elif veff >= 16:
                    result = 2.17
                elif veff >= 15:
                    result = 2.18
                elif veff >= 14:
                    result = 2.20
                elif veff >= 13:
                    result = 2.21
                elif veff >= 12:
                    result = 2.23
                elif veff >= 11:
                    result = 2.25
                elif veff >= 10:
                    result = 2.28
                elif veff >= 8:
                    result = 2.37
                elif veff >= 7:
                    result = 2.43
                elif veff >= 6:
                    result = 2.52
                elif veff >= 5:
                    result = 2.65
                elif veff >= 4:
                    result = 2.87
                elif veff >= 3:
                    result = 3.31
                elif veff >= 2:
                    result = 4.53
                elif veff >= 1:
                    result = 13.97
        else:
            result = MU_NAN
        return result

    def MUPruefverfahren_U(self):
        k = self.Erweiterungsfaktor_k()
        uy = self.StandardUnsicherheit_Uy()
        if k != MU_NAN and uy != MU_NAN:
            return k * uy
        return MU_NAN

    def BerechnungToleranzfaktor(self):
        u = self.MUPruefverfahren_U()
        og = 0  # Setze dies mit der tatsächlichen Logik
        ug = 0  # Setze dies mit der tatsächlichen Logik
        if u != MU_NAN and og != MU_NAN and ug != MU_NAN and og != ug:
            return (2 * u) / ((og - ug) * 1000) * 100
        return MU_NAN
