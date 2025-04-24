from app.services.component_service.component_abstract import MU_NAN, TMU_Komponente


class TMU_3DKomponente(TMU_Komponente):
    def __init__(self, modell, komp_id, const_list, formel):
        super().__init__(modell, komp_id, const_list, formel)
        self.const_needed = ["TC_3d_KMG_A"]
        self.c1_val = self.sensititivty_c1()
        self.c2_val = 0
        self.copy_source = None

    def a_val(self) -> float:
        return self.standard_unsicherheit_su()

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval
        elif self.data.TermL0 != 0:
            return self.data.TermL0
        else:
            a = 1  # muss eingegeben werden, vermutlich 'Konstanter Teil A' vom KMG
            return a / 3 if a != MU_NAN else MU_NAN

    def is_valid(self) -> bool:
        f = self.fields_to_edit
        return (
            ("EF_Term0" not in f or self.data.TermL0 != MU_NAN)
            and (
                "EF_Verteilung" not in f
                or self.data.Verteilung.name != "Verteilung_Undefiniert"
            )
            and (
                "EF_Kennwertart" not in f
                or self.data.KennwertArt.name != "KennwertArt_Undefiniert"
            )
        )

    @property
    def effektiver_freiheitsgrad(self) -> float:
        return self.arch_data.frei_eff if self.archiv else 1000

    def b_val(self) -> float:
        return self.arch_data.bval if self.archiv else 1

    def g_val(self) -> float:
        return 1.0

    def copy_methode(self, komp):
        self.copy_source = self.mymodell.find_komp(self.ckomponenten[komp])
        if self.sensititvity_c1 != MU_NAN and self.copy_source:
            self.data.KennwertArt = self.copy_source.data.kennwert_art
            self.data.TermL1 = self.copy_source.data.term_l1

    def anzahl_messungen(self) -> int:
        return round(self.data.TermL1)

    def messpunkt_anzahl(self) -> int:
        return self.data.frei_n_minus_1

    def tabelle1_su(self, l: float) -> float:
        if self.archiv:
            return self.arch_data.stdu
        if l == MU_NAN:
            return MU_NAN
        verteilung = self.data.Verteilung.name
        art = self.data.KennwertArt.name

        if verteilung == "V3D_Rechteck":
            if art == "K_HalbWeite":
                return l / (3**0.5)
            if art == "K_Spannweite":
                return l / (2 * (3**0.5))
            if art == "K_Standardabweichung":
                return l

        elif verteilung == "V3D_Normal":
            if art == "K_HalbWeite":
                return l / 2
            if art == "K_Spannweite":
                return l / 4
            if art == "K_Standardabweichung":
                return l

        elif verteilung == "V3d_Dreieck":
            if art == "K_HalbWeite":
                return l / (6**0.5)
            if art == "K_Spannweite":
                return l / (2 * (6**0.5))
            if art == "K_Standardabweichung":
                return l

        return MU_NAN

    def standard_unsicherheit_su(self) -> float:
        if self.archiv:
            return self.arch_data.aval
        elif self.data.TermL0 != 0:
            return self.data.TermL0
        else:
            a = 1  # muss eingegeben werden, vermutlich 'Konstanter Teil A' vom KMG hab ich aber nochmal
            return a / 3 if a != MU_NAN else MU_NAN

    @property
    def unsicherheitsbeitrag(self) -> float:
        if self.archiv:
            return self.arch_data.unsb
        siai = self.standard_unsicherheit_su()
        b = self.b_val()
        g = self.g_val()
        ci = self.c1_val
        if all(val != MU_NAN for val in [siai, b, g, ci]):
            return siai * b * g * ci
        return MU_NAN

    def mindestpunkt_anzahl(self, element: str) -> int:
        mapping = {
            "E3D_Punkt": 1,
            "E3D_Gerade": 2,
            "E3D_Ebene": 3,
            "E3D_Kreis": 3,
            "E3D_Halbkugel": 4,
            "E3D_Zylinder": 5,
            "E3D_Kegel": 6,
        }
        return mapping.get(element, 0)
