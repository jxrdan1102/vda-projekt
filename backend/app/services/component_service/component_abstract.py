import math
from abc import abstractmethod
from typing import Optional, List
from app.services.component_service.EverythinForComponents.TMU_Atom import TMU_Atom

from app.services.component_service.EverythinForComponents.TMU_Modell import TMU_Modell

from app.services.component_service.EverythinForComponents import TMU_ConstList

from app.services.component_service.EverythinForComponents.TMuKompRec import TKompConstantSet

from app.services.component_service.EverythinForComponents.TMuKompRec import TKompEditFieldsSet

from app.services.component_service.EverythinForComponents.TMuKompRec import TAuswertungsArchiv

from app.services.component_service.EverythinForComponents import TMuKompRec

MU_NAN = math.nan

class TMU_Komponente(TMU_Atom):

    def __init__(self, AModell: TMU_Modell, AnID: int, AConstList: TMU_ConstList, AFormel: str):
        super().__init__( AnID, "Komponente")
        self.modell: object = AModell
        self.const_list: object = AConstList
        self.formel: str = AFormel
        self.modl_txt_id: int = 0
        self.komp_txt_id: int = 0
        self.data: Optional[TMuKompRec] = None
        self.arch_data: Optional[TAuswertungsArchiv] = None
        self.freikat_text: str = ""
        self.c1_val: float = 0.0
        self.c2_val: float = 0.0
        self.const_needed: Optional[TKompConstantSet] = None
        self.fields_to_edit: Optional[TKompEditFieldsSet] = None
        self.position: int = 0
        self.einheit_ergebnis: str = ""

    def asciiformel(self) -> str:
        return self.formel

    def clear(self):
        # Initialize or reset data attributes
        self.data = {
            'TermL0': MU_NAN,
            'TermL1': MU_NAN,
            'Verteilung': 'Verteilung_Undefiniert',
            'KennwertArt': 'KennwertArt_Undefiniert',
            'Freiheitsgrad': 'Freiheitsgrad_Undefiniert',
            'FreiN_minus_1': 0,
            'Flags': 1,  # MU_USECOMP Vorbelgung: Komponente wird benötigt und zwar ein Mal.
        }

    def is_valid(self):
        data = self.data
        result = ((not 'EF_Term0' in self.FieldsToEdit) or (data['TermL0'] != MU_NAN)) and \
                 ((not 'EF_Term1' in self.FieldsToEdit) or (data['TermL1'] != MU_NAN)) and \
                 ((not 'EF_Verteilung' in self.FieldsToEdit) or (data['Verteilung'] != 'Verteilung_Undefiniert')) and \
                 ((not 'EF_Kennwertart' in self.FieldsToEdit) or (data['KennwertArt'] != 'KennwertArt_Undefiniert')) and \
                 ((not 'EF_Freheitsgrad' in self.FieldsToEdit) or (
                             data['Freiheitsgrad'] != 'Freiheitsgrad_Undefiniert'))

        if data['Freiheitsgrad'] == 'FG_N_Minus1':
            result = result and (data['FreiN_minus_1'] > 0)
        return result

    def std_unsicherheit(self, l: float) -> float:
        if l != MU_NAN:
            # Check distribution and return appropriate uncertainty
            if self.data.Verteilung == 'V_Rechteck':
                if self.data.KennwertArt == 'K_HalbWeite':
                    return l / math.sqrt(3)
                elif self.data.KennwertArt == 'K_Spannweite':
                    return l / (2 * math.sqrt(3))
                elif self.data.KennwertArt == 'K_Standardabweichung':
                    return l
            elif self.data.Verteilung == 'V_Normal':
                if self.data.KennwertArt == 'K_HalbWeite':
                    return l / 2
                elif self.data.KennwertArt == 'K_Spannweite':
                    return l / 4
                elif self.data.KennwertArt == 'K_Standardabweichung':
                    return l
            elif self.data.Verteilung == 'V_Dreieck':
                if self.data.KennwertArt == 'K_HalbWeite':
                    return l / math.sqrt(6)
                elif self.data.KennwertArt == 'K_Spannweite':
                    return l / (2 * math.sqrt(6))
                elif self.data.KennwertArt == 'K_Standardabweichung':
                    return l
        return MU_NAN

    def a_val(self) -> float:
        return self.data.TermL0

    def b_val(self) -> float:
        return self.data.TermL1

    def std_unsicherheit_l0(self) -> float:
        return self.std_unsicherheit(self.a_val())

    def std_unsicherheit_l1(self) -> float:
        return self.std_unsicherheit(self.b_val())

    def sensititivty_c1(self) -> float:
        return self.c1_val

    def sensititivty_c2(self) -> float:
        return self.c2_val

    def effektiver_freiheitsgrad(self) -> float:
        if self.data['Freiheitsgrad'] == 'FG_unbegrenzt':
            return 1000
        elif self.data['Freiheitsgrad'] == 'FG_N_Minus1':
            if self.data['FreiN_minus_1'] > 0:
                return self.data['FreiN_minus_1']
            return MU_NAN
        return MU_NAN

    def unsicherheitsbeitrag_l0(self) -> float:
        su = self.std_unsicherheit(self.a_val())
        c1 = self.sensititivty_c1()
        if su != MU_NAN and c1 != MU_NAN:
            return su * c1
        return MU_NAN

    def unsicherheitsbeitrag_l1(self) -> float:
        su = self.std_unsicherheit(self.b_val())
        c2 = self.sensititivty_c2()
        l = 25 * 1000  # Messwert in mm Berechnung in µm
        if su != MU_NAN and c2 != MU_NAN and l != MU_NAN:
            return su * c2 * l
        return MU_NAN

    def unsicherheitsbeitrag(self) -> float:
        su0 = self.unsicherheitsbeitrag_l0()
        su1 = self.unsicherheitsbeitrag_l1()
        if su0 != MU_NAN and su1 != MU_NAN:
            return math.sqrt(self.data.Flags) * (abs(su0) + abs(su1))
        return MU_NAN

    def varianz(self) -> float:
        ub = self.unsicherheitsbeitrag()
        if ub != MU_NAN:
            return ub ** 2
        return MU_NAN

    def prep_archiv(self):
        self.arch_data = {
            'AVAL': self.a_val(),
            'BVAL': self.b_val(),
            'ASUL0': self.std_unsicherheit_l0(),
            'ASUL1': self.std_unsicherheit_l1(),
            'SensC1': self.sensititivty_c1(),
            'SensC2': self.sensititivty_c2(),
            'FreiEff': self.effektiver_freiheitsgrad(),
            'UNSBL0': self.unsicherheitsbeitrag_l0(),
            'UNSBL1': self.unsicherheitsbeitrag_l1(),
            'UnsB': self.unsicherheitsbeitrag(),
            'VARIANZ': self.varianz()
        }

    # Placeholder for database load and save functions (to be implemented)
    def db_load(self, analyse_id: int):
        pass

    def db_save(self, analyse_id: int):
        pass

    def debug_str(self, s: List[str]) -> bool:
        s.append("Berechnete Daten:")  # For simplicity
        return False

    def debug_grid(self, grid: List[List[str]]) -> bool:
        grid.append(["Daten", "Werte"])
        return False