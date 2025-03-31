from enum import Enum

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants


class TMuKompRec:
    def __init__(self, TermL0, TermL1, Verteilung, KennwertArt, Freiheitsgrad, FreiN_minus_1, Flags):
        self.TermL0 = TermL0
        self.TermL1 = TermL1
        self.Verteilung = Verteilung
        self.KennwertArt = KennwertArt
        self.Freiheitsgrad = Freiheitsgrad
        self.FreiN_minus_1 = FreiN_minus_1
        self.Flags = Flags

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