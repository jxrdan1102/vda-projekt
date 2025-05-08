import math
from math import pi, sqrt

from app.services.component_service.EverythinForComponents.TMU_ConstList import TKompConstants
from app.services.component_service.EverythinForComponents.TMuKompRec import TMuKompRec
from app.services.component_service.component_abstract import MU_NAN
from app.services.component_service.componente3D import TMU_3DKomponente


class TMU_3dKomponente_Richtung(TMU_3DKomponente):
    def __init__(self, modell, komp_id, const_list, formel):
        super().__init__(modell, komp_id, const_list, formel)

    @property
    def unsicherheitsbeitrag(self):
        result = MU_NAN

        if self.archiv:
            result = self.ArchData.UNSB
        else:
            ux = MU_NAN
            print("hier testi",self.c1_val)
            if self.c1_val != MU_NAN:
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    ux = self.standard_unsicherheit
                else:
                    A = 1
                    si = self.standard_unsicherheit_su()
                    if si != MU_NAN:
                        ux = si
                    elif A != MU_NAN:
                        ux = A / 3
            if ux != MU_NAN and self.b_val != MU_NAN and self.c1_val != MU_NAN:

                result = ux * self.b_val() * self.sensititivty_c1()
                print("testtiii", result,self.b_val(),self.sensititivty_c1(), self)
        return result

    def unsicherheitsbeitrag_alternative(self):
        return self.unsicherheitsbeitrag()

    @property
    def effektiver_freiheitsgrad(self):
        result = MU_NAN

        if self.archiv:
            result = self.ArchData.FreiEff
        else:
            print("lemme",self, self.data.KennwertArt, self.messpunkt_anzahl)
            if self.data.KennwertArt.name == "M3D_MethodeB":
                result = self.messpunkt_anzahl - 1
            else:

                result = self.anzahl_messungen() * (self.messpunkt_anzahl - 2)
                print("hierlemme",self.anzahl_messungen())
        if result != MU_NAN:
            result = abs(result)
        print("resr",self, result)
        return result


def in_grad(bogen: float) -> float:
    return bogen * (180 / pi)


class TK_3d_ResKMG(TMU_3DKomponente):
    def __init__(self, modell, const_list,lfdnr):
        super().__init__(modell, 1378, const_list, "&Delta;I<sub>KMG;R</sub>")
        self.lfdnr = lfdnr
        self.einheit = "µm"
        self.einheit_ergebnis = "µm"
        self.dez = 5
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_AUFLOES"],]
        self.fields_to_edit = []
        self.id: int
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="K_HalbWeite",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.messpunkt_anzahl = None
        self.addConstNeededToModell()

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.sens_c1
        return 1.0

    def b_val(self) -> float:
        return 1.0

    def standard_unsicherheit_su(self) -> float:
        i = 2
        if i != MU_NAN:
            return i / (3**0.5)
        return MU_NAN


class modelll:
    def __init__(self, element1_3d, winkel_e1_3d):
        self.element1_3d = element1_3d
        self.winkel_e1_3d = winkel_e1_3d


class TK_3d_Wi_WE(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list,lfdnr):
        super().__init__(modell, 1379, const_list, "W<sub>E</sub>")
        self.einheit = "µm"
        self.lfdnr = lfdnr
        self.einheit_ergebnis = "rad"
        self.dez = 5
        self.ConstNeeded += [TKompConstants["TC_3d_Ri_LME"],TKompConstants["TC_3d_Ri_LE"],]
        self.fields_to_edit = ["EF_Term0", "EF_Kennwertart", "EF_MPAnzahl"]
        self.messpunkt_anzahl = None
        self.id: int
        self.data = TMuKompRec(
            TermL0=0.0,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.addConstNeededToModell()

    def b_val(self) -> float:
        if self.archiv:
            return self.arch_data.bval
        result = MU_NAN
        print(self.modell.Element1, self.data.KennwertArt.name, self, "hilfe", self.messpunkt_anzahl)
        if self.data.KennwertArt.name == "M3D_MethodeA":
            if self.modell.Element1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
                result = 1.0
        elif self.messpunkt_anzahl > 0:
            if self.modell.Element1 in ["Gerade", "Ebene"]:
                print("hierrr",self.modell.punktmuster)
                if self.modell.punktmuster == 1:
                    result = sqrt((12 * (4 - 1)) / (4 * (4 + 1)))
                elif self.modell.punktmuster  == 2:
                    result = sqrt(4 / 4)
                elif self.modell.punktmuster  == 3:
                    result = sqrt(8 / self.messpunkt_anzahl)

            elif self.modell.Element1 in ["Zylinder", "Kegel"]:
                if self.modell.punktmuster  == 1:
                    result = sqrt(
                        (24 * (self.messpunkt_anzahl - 1))
                        / (self.messpunkt_anzahl * (self.messpunkt_anzahl + 1))
                    )
                elif self.modell.punktmuster  == 2:
                    result = sqrt(8 / self.messpunkt_anzahl)
        return result

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval

        sab = MU_NAN
        lme = 2

        if self.data.KennwertArt.name == "M3D_MethodeA":
            if self.data.TermL0 != 0:
                sab = self.data.TermL0
        else:
            if self.data.TermL0 != 0:
                sab = self.data.TermL0
            else:
                a = 1
                if a != MU_NAN:
                    sab = a / 3.0
        if sab != MU_NAN and lme != MU_NAN and lme != 0:
            result = (3 * sab * 0.001) / lme
            return result / sqrt(3)
        return MU_NAN

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.arch_data.sens_c1

        if self.modell.Element1 not in ["Punkt", "Kreis"]:
            lme = 2
            le = 2
            if le != MU_NAN and lme != MU_NAN and lme != 0:
                return in_grad(le / lme)
        return MU_NAN


class TK_3d_Wi_WB(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list, lfdnr):
        super().__init__(modell, 1380, const_list, "&Delta;I<sub>KMG;R</sub>")
        self.lfdnr = lfdnr
        self.my_modell = modelll("Gerade", 1)
        self.id: int
        self.archiv = None
        self.modell = modell
        self.messpunkt_anzahl = None
        self.lmb = 2
        self.lb = 2
        self.a = 1
        self.c1_val = 1
        self.result = None
        self.ConstNeeded += [TKompConstants["TC_3d_Ri_LMB"],TKompConstants["TC_3d_Koax_LB"],TKompConstants["TC_3d_KMG_A"],]
        self.MU_NAN = float("nan")
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.addConstNeededToModell()

    def in_grad(self, bog: float) -> float:
        return bog * (180 / math.pi)

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.archiv_data_sens_c1()
        else:
            if self.modell.Bezug1 in ["Gerade", "Ebene", "Zylinder", "Kegel"]:
                if self.lmb is not None and self.lb is not None and self.lmb != 0:
                    return self.in_grad(self.lb / self.lmb)
        return MU_NAN

    def b_val(self) -> float:
        if self.archiv:
            return self.archiv_data_bval()
        else:
            if self.sensititivty_c1() != MU_NAN:
                if self.data.KennwertArt.name == "M3D_MethodeA":
                    if self.modell.Element1 in [
                        "Gerade",
                        "Ebene",
                        "Zylinder",
                        "Kegel",
                    ]:
                        return 1
                else:
                    print ("jojojo", self.modell.Element1, self.modell.Bezug1,)
                    if self.messpunkt_anzahl > 1:
                        if self.modell.Element1 in ["Gerade", "Ebene"]:
                            if self.modell.Bezug1 in ["Punkt", "NDEF"]:
                                return math.sqrt(
                                    (12 * (self.messpunkt_anzahl - 1))
                                    / (
                                        self.messpunkt_anzahl
                                        * (self.messpunkt_anzahl + 1)
                                    )
                                )
                            elif self.modell.Bezug1 == "Gerade":
                                return math.sqrt(4 / self.messpunkt_anzahl)
                            elif self.modell.Bezug1 == "Ebene":
                                return math.sqrt(8 / self.messpunkt_anzahl)
                        elif self.modell.Element1 in ["Zylinder", "Kegel"]:
                            if self.modell.Bezug1 in ["Punkt", "Kegel"]:
                                return math.sqrt(
                                    (24 * (self.messpunkt_anzahl - 1))
                                    / (
                                        self.messpunkt_anzahl
                                        * (self.messpunkt_anzahl + 1)
                                    )
                                )
                            elif self.modell.Bezug1 == "Gerade":
                                return math.sqrt(8 / self.messpunkt_anzahl)
        return self.MU_NAN

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.archiv_data_aval()
        else:
            sab = MU_NAN
            if self.data.KennwertArt.name == "M3D_MethodeA":
                if self.data.TermL0 != 0:
                    sab = self.data.TermL0
            else:
                if self.data.TermL0 != 0:
                    sab = self.data.TermL0
                else:
                    if self.a is not None:
                        sab = self.a / 3

            if sab != MU_NAN and self.lmb != self.MU_NAN and self.lmb != 0:
                result = (3 * sab * 0.001) / self.lmb
                if result != self.MU_NAN:
                    return result / math.sqrt(3)
        return self.MU_NAN

    @property
    def effektiver_freiheitsgrad(self) -> float:
        if self.archiv:
            return self.archiv_data_frei_eff()
        else:
            if self.data.KennwertArt.name == "M3D_MethodeB":
                return max(0, self.messpunkt_anzahl - 1)
            else:
                return max(0, self.messpunkt_anzahl - self.mindest_punkt_anzahl())

    def archiv_data_sens_c1(self):
        return 1.0

    def archiv_data_bval(self):
        return 1.0

    def archiv_data_aval(self):
        return 1.0

    def archiv_data_frei_eff(self):
        return 1.0

    def mindest_punkt_anzahl(self):
        return 2


class TK_3d_Wi_DeltaEKMG(TMU_3dKomponente_Richtung):
    def __init__(self, modell, const_list,lfdnr):
        super().__init__(modell, 1381, const_list, "&Delta;I<sub>KMG;R</sub>")
        self.messpunkt_anzahl = None
        self.archiv = None
        self.lfdnr = lfdnr
        self.id: int
        self.k = 1
        self.alpha = 2
        self.le = 2
        self.lb = 2
        self.MU_NAN = float("nan")
        self.c1_val = 1
        self.ConstNeeded += [TKompConstants["TC_3d_KMG_K"],TKompConstants["TC_3d_Ri_LE"],TKompConstants["TC_3d_Ri_LME"],TKompConstants["TC_3d_Koax_LB"],TKompConstants["TC_3d_Ri_Alpha"],]
        self.result = None
        self.data = TMuKompRec(
            TermL0=0.15,
            TermL1=0,
            Verteilung="V_Rechteck",
            KennwertArt="M3D_MethodeB",
            Freiheitsgrad="FG_unbegrenzt",
            FreiN_minus_1=0,
            Flags=1,
        )
        self.addConstNeededToModell()

    def in_grad(self, bog: float) -> float:
        return bog * (180 / math.pi)

    def sensititivty_c1(self) -> float:
        if self.archiv:
            return self.archiv_data_sens_c1()
        else:
            if self.le is not None and self.lb is not None and self.lb != 0:
                return self.in_grad(self.le / self.lb)
        return self.MU_NAN

    def standard_unsicherheit_su(self) -> float:

        if self.archiv:
            return self.archiv_data_aval()
        else:
            if self.k != 0 and self.k != self.MU_NAN:
                result = ((2 * 0.001) / self.k) * math.pow(
                    math.sin(self.in_rad(self.alpha)), 2
                )
                if result != self.MU_NAN:
                    return result / (2 * math.sqrt(3))
        return self.MU_NAN

    def b_val(self) -> float:
        if self.archiv:
            return self.archiv_data_bval()
        else:
            return 1

    def in_rad(self, grad: float) -> float:
        return grad * (math.pi / 180)

    def archiv_data_sens_c1(self):
        return 1.0

    def archiv_data_aval(self):
        return 1.0

    def archiv_data_bval(self):
        return 1.0
