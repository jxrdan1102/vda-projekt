import math
from abc import abstractmethod
from typing import Optional, List
from app.services.component_service.EverythinForComponents.TMU_Atom import TMU_Atom

from app.services.component_service.EverythinForComponents import TMU_ConstList

from app.services.component_service.EverythinForComponents.TMuKompRec import TKompConstantSet

from app.services.component_service.EverythinForComponents.TMuKompRec import TKompEditFieldsSet

from app.services.component_service.EverythinForComponents.TMuKompRec import TAuswertungsArchiv

from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants

from app.services.component_service.EverythinForComponents.TMuKompRec import TMU_Verteilung, TMU_Freiheitsgrad, \
    TMU_KennwertArt

MU_NAN = math.nan

class TMU_Komponente(TMU_Atom):

    def __init__(self, AModell: 'TMU_Modell', AnID: int, AConstList: TMU_ConstList, AFormel: str):
        super().__init__( AnID, "Komponente")
        self.data = TMuKompRec(TermL0=MU_NAN,
            TermL1=MU_NAN,
            Verteilung="Verteilung_Undefiniert",  # String-Wert wird akzeptiert
            KennwertArt="KennwertArt_Undefiniert",  # String-Wert wird akzeptiert
            Freiheitsgrad="Freiheitsgrad_Undefiniert",  # String-Wert wird akzeptiert
            FreiN_minus_1=0,
            Flags=1)
        self.modell: object = AModell
        self.const_list: object = AConstList
        self.formel: str = AFormel
        self.modl_txt_id: int = 0
        self.komp_txt_id: int = 0
        self.arch_data: Optional[TAuswertungsArchiv] = None
        self.ConstNeeded: List[TKompConstants]= [TKompConstants["TC_Messwert"]]
        print(self.ConstNeeded)
        self.freikat_text: str = ""
        self.c1_val: float = 1
        self.c2_val: float = 1
        self.fields_to_edit: Optional[TKompEditFieldsSet] = None
        self.position: int = 0
        self.einheit_ergebnis: str = ""
        self.clear()

    def setData(self, data: TMuKompRec):
        self.data = data

    def asciiformel(self) -> str:
        return self.formel

    def addConstNeededToModell(self):
        if self.modell is not None:
            for const in self.ConstNeeded:
                print(const)
                self.modell.const_needed.add(const)
                self.modell.const_list.const_map[const] = None


    def clear(self):
        self.data = TMuKompRec(TermL0=MU_NAN,
                   TermL1=MU_NAN,
                   Verteilung="Verteilung_Undefiniert",  # String-Wert wird akzeptiert
                   KennwertArt="KennwertArt_Undefiniert",  # String-Wert wird akzeptiert
                   Freiheitsgrad="Freiheitsgrad_Undefiniert",  # String-Wert wird akzeptiert
                   FreiN_minus_1=0,
                   Flags=1)

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
        print("hilf mir",l)
        if l != MU_NAN:
            print("hilf mir nochmal",self.data.Verteilung.name)
            # Check distribution and return appropriate uncertainty
            if self.data.Verteilung.name == 'V_Rechteck':
                if self.data.KennwertArt.name == 'K_HalbWeite':
                    print("1", l / math.sqrt(3))
                    return l / math.sqrt(3)
                elif self.data.KennwertArt.name == 'K_Spannweite':
                    print("wurzel",l / (2 * math.sqrt(3)))
                    return l / (2 * math.sqrt(3))
                elif self.data.KennwertArt.name == 'K_Standardabweichung':
                    return l
            elif self.data.Verteilung.name == 'V_Normal':
                if self.data.KennwertArt.name == 'K_HalbWeite':
                    return l / 2
                elif self.data.KennwertArt.name == 'K_Spannweite':
                    return l / 4
                elif self.data.KennwertArt.name == 'K_Standardabweichung':
                    return l
            elif self.data.Verteilung.name == 'V_Dreieck':
                if self.data.KennwertArt.name == 'K_HalbWeite':
                    return l / math.sqrt(6)
                elif self.data.KennwertArt.name == 'K_Spannweite':
                    return l / (2 * math.sqrt(6))
                elif self.data.KennwertArt.name == 'K_Standardabweichung':
                    return l
        print("problem std_unsicherheit", self.data.Verteilung.name)
        return MU_NAN

    def a_val(self) -> float:
        print("Zeig mirs ",self.data.TermL0)
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
        if self.data.Freiheitsgrad.name == 'FG_unbegrenzt':
            self.EffektiverFreiheitsgrad = 1000
            return 1000
        elif self.data.Freiheitsgrad.name == 'FG_N_Minus1':
            if self.data.FreiN_minus_1 > 0:
                self.EffektiverFreiheitsgrad = self.data.FreiN_minus_1
                return self.data.FreiN_minus_1
            return MU_NAN
        return MU_NAN

    def unsicherheitsbeitrag_l0(self) -> float:
        su = self.std_unsicherheit(self.a_val())
        c1 = self.sensititivty_c1()
        print("fuck man", su,c1, self.a_val())
        if su != MU_NAN and c1 != MU_NAN:
            return su * c1
        return MU_NAN

    def unsicherheitsbeitrag_l1(self) -> float:
        su = self.std_unsicherheit(self.b_val())
        c2 = self.sensititivty_c2()
        print("simma",su,c2)
        l = 25 * 1000  # Messwert in mm Berechnung in µm
        if su != MU_NAN and c2 != MU_NAN and l != MU_NAN:
            return su * c2 * l
        return MU_NAN

    def unsicherheitsbeitrag(self) -> float:
        su0 = self.unsicherheitsbeitrag_l0()
        print("geht noch", su0)
        print("bval",self.b_val())
        su1 = self.unsicherheitsbeitrag_l1()
        print("geht noch2", su1)
        if su0 != MU_NAN and su1 != MU_NAN:
            if self.id == 4 or self.id == 6:
                self.data.Flags = 2
            return math.sqrt(self.data.Flags) * (abs(su0) + abs(su1))
        return MU_NAN

    def varianz(self) -> float:
        ub = self.unsicherheitsbeitrag()
        print("componente = ",self,ub)
        if not math.isnan(ub):
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