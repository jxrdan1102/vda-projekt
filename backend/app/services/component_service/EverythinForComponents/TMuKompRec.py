from enum import Enum

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants

class TMU_Verteilung(Enum):
    Verteilung_Undefiniert = 1
    V_Rechteck = 2
    V_Normal = 3
    V_Dreieck = 4
    V3D_Rechteck = 5
    V3D_Normal = 6
    V3d_Dreieck = 7
    V3D_Arcsin = 8
    V3D_AnzahlMP = 9
    V3D_Stdabw = 10

class TMU_KennwertArt(Enum):
    KennwertArt_Undefiniert = 1
    K_HalbWeite = 2
    K_Spannweite = 3
    K_Standardabweichung = 4
    M3D_MethodeA = 5
    M3D_MethodeB = 6
    M3D_MethodeAnzahlPunkte = 7

class TMU_Freiheitsgrad(Enum):
    Freiheitsgrad_Undefiniert = 1
    FG_unbegrenzt = 2
    FG_N_Minus1 = 3

class TMuKompRec:
    def __init__(self, TermL0, TermL1, Verteilung, KennwertArt, Freiheitsgrad, FreiN_minus_1, Flags):
        self.TermL0: float = TermL0
        self.TermL1: float = TermL1
        self.Verteilung: TMU_Verteilung = Verteilung
        self.KennwertArt: TMU_KennwertArt = KennwertArt
        self.Freiheitsgrad:TMU_Freiheitsgrad = Freiheitsgrad
        self.FreiN_minus_1: int = FreiN_minus_1
        self.Flags: int = Flags

    def to_dict(self):
        return {
            'TermL0': self.TermL0,
            'TermL1': self.TermL1,
            'Verteilung': self.Verteilung,
            'KennwertArt': self.KennwertArt,
            'Freiheitsgrad': self.Freiheitsgrad,
            'FreiN_minus_1': self.FreiN_minus_1,
            'Flags': self.Flags
        }

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