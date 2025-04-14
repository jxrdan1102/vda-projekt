from enum import Enum
from typing import Union

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from pydantic import BaseModel, validator, root_validator


# Enum-Klassen mit den angegebenen Werten

# Enum-Klassen
class TMU_Verteilung(Enum):
    Verteilung_Undefiniert = 0
    V_Rechteck = 1
    V_Normal = 2
    V_Dreieck = 3
    V3D_Rechteck = 4
    V3D_Normal = 5
    V3d_Dreieck = 6
    V3D_Arcsin = 7
    V3D_AnzahlMP = 8
    V3D_Stdabw = 9

    @classmethod
    def _get_value(cls, value: Union[int, str]):
        if isinstance(value, int):
            return cls(value)
        elif isinstance(value, str):
            return cls[value]
        raise ValueError(f"Invalid value: {value}, expected integer or string")


class TMU_KennwertArt(Enum):
    KennwertArt_Undefiniert = 0
    K_HalbWeite = 1
    K_Spannweite = 2
    K_Standardabweichung = 3
    M3D_MethodeA = 4
    M3D_MethodeB = 5
    M3D_MethodeAnzahlPunkte = 6

    @classmethod
    def _get_value(cls, value: Union[int, str]):
        if isinstance(value, int):
            return cls(value)
        elif isinstance(value, str):
            return cls[value]
        raise ValueError(f"Invalid value: {value}, expected integer or string")


class TMU_Freiheitsgrad(Enum):
    Freiheitsgrad_Undefiniert = 0
    FG_unbegrenzt = 1
    FG_N_Minus1 = 2

    @classmethod
    def _get_value(cls, value: Union[int, str]):
        if isinstance(value, int):
            return cls(value)
        elif isinstance(value, str):
            return cls[value]
        raise ValueError(f"Invalid value: {value}, expected integer or string")


# Model mit Enums und Serialisierung
class TMuKompRec(BaseModel):
    TermL0: float
    TermL1: float
    Verteilung: TMU_Verteilung
    KennwertArt: TMU_KennwertArt
    Freiheitsgrad: TMU_Freiheitsgrad
    FreiN_minus_1: int
    Flags: int

    @root_validator(pre=True)
    def parse_enums(cls, values):
        values['Verteilung'] = TMU_Verteilung._get_value(values.get('Verteilung'))
        values['KennwertArt'] = TMU_KennwertArt._get_value(values.get('KennwertArt'))
        values['Freiheitsgrad'] = TMU_Freiheitsgrad._get_value(values.get('Freiheitsgrad'))
        return values

    class Config:
        json_encoders = {
            TMU_Verteilung: lambda v: v.name,
            TMU_KennwertArt: lambda v: v.name,
            TMU_Freiheitsgrad: lambda v: v.name,
        }
class TMuKompRecW:
    def __init__(self):
        self.TermL0:float
        self.TermL1: float
        self.Verteilung: Union[int, str]
        self.KennwertArt: Union[int, str]
        self.Freiheitsgrad: Union[int, str]
        self.FreiN_minus_1: int
        self.Flags: int

class TAuswertungsArchiv:
    def __init__(self, STDU, AVAL, BVAL, ASUL0, ASUL1, SensC1, SensC2, FreiEff, UNSBL0, UNSBL1, UnsB, VARIANZ):
        self.STDU = STDU
        self.AVAL = AVAL
        self.BVAL = BVAL
        self.ASUL0 = ASUL0
        self.ASUL1 = ASUL1
        self.SensC1 = SensC1
        self.SensC2 = SensC2
        self.FreiEff = FreiEff
        self.UNSBL0 = UNSBL0
        self.UNSBL1 = UNSBL1
        self.UnsB = UnsB
        self.VARIANZ = VARIANZ

def MU_FloatToStr(f: float) -> str:
    return str(f)

def MU_FloatToStrF(f: float, digits: int) -> str:
    return f"{f:.{digits}f}"

def KomponentTitle(kompID: int) -> str:
    titles = {
        1: "Messbereich",
        2: "Nennmaß",
        3: "Unteres Abmaß",
        4: "Oberes Abmaß",
        5: "Einheit",
        # Füge weitere Titel hinzu...
    }
    return titles.get(kompID, "Unbekannt")

def ConstTitle(ConstID: TKompConstants) -> str:
    titles = {
        TKompConstants.TC_Messbereich: "Messbereich",
        TKompConstants.TC_Nennmass: "Nennmaß",
        TKompConstants.TC_UntAbmass: "Unteres Abmaß",
        TKompConstants.TC_ObAbmass: "Oberes Abmaß",
        TKompConstants.TC_Einheit: "Einheit",
        # Füge weitere Konstanten hinzu...
    }
    return titles.get(ConstID, "Unbekannt")

class TKompEditFields(Enum):
    EF_Term0 = 1
    EF_Term1 = 2
    EF_Verteilung = 3
    EF_Kennwertart = 4
    EF_Freheitsgrad = 5
    EF_MPAnzahl = 6
    EF_StreuungsParam = 7

TKompEditFieldsSet = set(TKompEditFields)

TKompConstantSet = set(TKompConstants)