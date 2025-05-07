from enum import Enum

from app.models.ANAMU import ANAKONST
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TKompConstants(Enum):
    TC_Messbereich = 1
    TC_Nennmass = 2
    TC_UntAbmass = 3
    TC_ObAbmass = 4
    TC_Einheit = 5
    TC_AusdehnKoeffME = 6
    TC_AusdehnKoeffEN = 7
    TC_AusdehnKoeffMO = 8
    TC_DurchmesserMessflaeche = 9
    TC_DurchmesserMesseinsatzME = 10
    TC_BreiteMessflaecheMO = 11
    TC_nicht_benutzt_BreiteMessflaecheGN = 12
    TC_BreiteMessflaecheEN = 13
    TC_FaktorKennlinieME = 14
    TC_ParameterKennlinieME = 15
    TC_NichtLinearKennlinieME = 16
    TC_Geometrie_ME = 17
    TC_Geometrie_MO = 18
    TC_Geometrie_GN = 19
    TC_Geometrie_BN = 20
    TC_MantellinieME = 21
    TC_MantellinieMO = 22
    TC_nicht_benutzt_TC_MantellinieGN = 23
    TC_MantellinieEN = 24
    TC_Messwert = 25
    TC_MesskraftME = 26
    TC_MesskraftSchwankungME = 27
    TC_NennmassEN = 28
    TC_nicht_benutzt_TC_NennmassGN = 29
    TC_TempME = 30
    TC_TempMO = 31
    TC_TempEN = 32
    TC_ZeitDeltaMessungEN_MO = 33
    TC_ZeitDrift = 34
    TC_DurchmesserEN = 35
    TC_Winkelabweichung_von_90_Grad = 36
    TC_Radius_der_Zone_des_Spiels = 37
    TC_Laenge_kurze_Kante_PEM = 38
    TC_Tol_Abw_Spanne_ISO_3650 = 39
    TC_Elast_Modul_Normal = 40
    TC_Elast_Modul_MO = 41
    TC_Poisson_Koeff_Normal = 42
    TC_Poisson_Koeff_MO = 43
    TC_Korrelationskoeffizient = 44
    TC_Schrittweite_Geradheitskalibrierung_EN = 45
    TC_Positionsgenauigkeit_Kalibrierung_MO = 46
    TC_Betrag_max_Abweichung_Bezugsgerade = 47
    TC_Laenge_stehender_Schenkel_EN = 48
    TC_Abstand_Stuetzpunkte_EN = 49
    TC_Geradheit_Messplatte_EN = 50
    TC_Positionsabweichung_Stuetzpunkte_EN = 51
    TC_Kalibrierung_Geradheit_EN = 52
    TC_Laenge_stehender_Schenkel_MO = 53
    TC_Stuetzpunktabstand_MO = 54
    TC_Geradheit_Messplatte_MO = 55
    TC_Positionsabweichung_Stuetzpunkte_MO = 56
    TC_Kalibrierung_Geradheit_MO = 57
    TC_Kalibrierung_Ebenheit_Messplatte = 58
    TC_Positionsgenauigkeit_Stuetzpunkte = 59
    TC_Schrittweite_Geradheitskalibrierung_MO = 60
    TC_Hoehendifferenz_Stuetzpunkte = 61
    TC_Laenge_Messobjekt = 62
    TC_Anzahl_Verschiebungen_MO = 63
    TC_Messbereichsendwert_Messeinrichtung = 64
    TC_Hoehe_zu_Rechtwinkligkeit = 65
    TC_Rh_Anzahl_Messwerte_pro_Teilmessstrecke = 66
    TC_Rh_Anzahl_Teilmessstrecken = 67
    TC_Rh_Ortabhaengige_Unsicherheit_in_y = 68
    TC_Rh_Gradient_in_Rillenrichtung = 69
    TC_Rh_Messpunktabstand = 70
    TC_Rh_Tiefpasswellenlaengen = 71
    TC_Rh_Kennwertaenderungsfaktor = 72
    TC_Rh_Gemessene_Kenngroesse = 73
    TC_Rh_Anzahl_Wiederholungsmessungen_geaenderter_Antastort = 74
    TC_Rh_Anzahl_Wiederholmessungen_selber_Antastort = 75
    TC_Fm_Anzahl_Wiederholmessungen_StreuungAnzeige = 76
    TC_Fm_Abstand_zwischen_zwei_benachbarten_Profilpunkten = 77
    TC_Fm_Grenzwellenlaenge = 78
    TC_Fm_Messwert_MO = 79
    TC_Fm_Richtiger_Wert_Rundheit_Kugelnormal = 80
    TC_Fm_Messunsicherheit_der_Kalibrierung_Kugelnormal = 81
    TC_Fm_Gemessenden_Exzentrizitaet = 82
    TC_Fm_Aussendurchmesser_MO = 83
    TC_Fm_Tastkugeldurchmesser = 84
    TC_Fm_Innendurchmesser_MO = 85
    TC_Fm_Kippung_MO_XAchse = 86
    TC_Fm_Kippung_MO_YAchse = 87
    TC_Fm_Radius_MO = 88
    TC_Fm_Neigung_Zylinderachse_MO_zu_Flaeche_XOY = 89
    TC_Fm_Formabweichung_Normal = 90
    TC_Fm_Kalibrierung_Normal = 91
    TC_Fm_Standardabweichung_Wiederholmessungen_Normal = 92
    TC_Fm_AnzahlMessungen_Fuehrungsabweichung = 93
    TC_Fm_Gemessene_Rundheit_EN = 94
    TC_KTMG_Gemessener_Abstand = 95
    TC_KTMG_Konstanter_Anteil_EMPE = 96
    TC_KTMG_Anzahl_Messpunkte = 97
    TC_KTMG_Gemessener_Winkel = 98
    TC_KTMG_Laenge_kleinster_Schenkel = 99
    TC_KTMG_Gemessene_Geradheit = 100
    TC_KTMG_Sektor_Kreis = 101
    TC_3d_KMG_A = 102
    TC_3d_KMG_K = 103
    TC_3d_KMG_Uc = 104
    TC_3d_KMG_alphaM = 105
    TC_3d_KMG_Tm = 106
    TC_3d_KMG_deltaTm = 107
    TC_3d_KMG_alphaW = 108
    TC_3d_KMG_Tw = 109
    TC_3d_KMG_deltaTw = 110
    TC_3d_DUME_D = 111
    TC_3d_DUME_alpha = 112
    TC_3d_DUME_l = 113
    TC_3d_FORM_L = 114
    TC_3d_FORM_DL = 115
    TC_3d_FORM_F = 116
    TC_3d_ABST_L = 117
    TC_3d_ABST_LM1 = 118
    TC_3d_ABST_LE1 = 119
    TC_3d_ABST_LM2 = 120
    TC_3d_ABST_LE2 = 121
    TC_3d_Ri_LA = 122
    TC_3d_Ri_Alpha = 123
    TC_3d_Ri_LME = 124
    TC_3d_Ri_LE = 125
    TC_3d_Ri_LMB = 126
    TC_3d_Sym_DE = 127
    TC_3d_Sym_LE = 128
    TC_3d_Sym_DB = 129
    TC_3d_Sym_LMB = 130
    TC_3d_Koax_DE = 131
    TC_3d_Koax_LE = 132
    TC_3d_Koax_LA = 133
    TC_3d_Koax_DB = 134
    TC_3d_Koax_LB = 135
    TC_3d_Koax_LMB = 136
    TC_3d_KoaxGA_DE = 137
    TC_3d_KoaxGA_LME = 138
    TC_3d_KoaxGA_LE = 139
    TC_3d_KoaxGA_LB = 140
    TC_3d_KMG_LT = 141
    TC_3d_DUME_LM = 142
    TC_3D_DUME_LS = 143
    TC_3D_ABST_LTE = 144
    TC_3D_ABST_LTB = 145
    TC_3d_Ri_LTE1 = 146
    TC_3d_Ri_LTE2 = 147
    TC_3d_Ri_LTB1 = 148
    TC_3d_Ri_LTB2 = 149
    TC_3d_Sym_LME = 150
    TC_3d_Sym_LB = 151
    TC_3d_Sym_LTE = 152
    TC_3d_Sym_LTB = 153
    TC_3d_Koax_LME = 154
    TC_3d_Koax_LT_entfaellt = 155
    TC_3d_Koax_LTB = 156
    TC_3d_Koax_LTE = 157
    TC_3d_KoaxGA_LA = 158
    TC_3d_KoaxGA_LTB = 159
    TC_3d_KoaxGA_LTE = 160
    TC_3d_KMG_MpeML = 161
    TC_Gewinde_Steigung = 162
    TC_3D_NennLaenge_LD = 163
    TC_3d_FORM_FN = 164
    TC_3d_FORM_FKMG = 165
    TC_3d_KMG_AUFLOES = 166
    TC_3d_PktPkt_dist = 167
    TC_3d_PktPkt_Wechsel = 168
    TC_3d_PktPkt_nTastBe = 169
    TC_3d_PktPkt_nTastTe = 170
    TC_3d_PktPkt_SigBe = 171
    TC_3d_PktPkt_SigTe = 172
    TC_3d_PktPkt_ScanKgl = 173
    TC_3d_PktPkt_MBe = 174
    TC_3d_PktPkt_Mte = 175
    TC_3d_PktPkt_Temp = 176
    TC_3d_PktPkt_Gamma0 = 177
    TC_3d_PktPkt_Gamma1 = 178
    TC_3d_PktPkt_WinkelSeg_BE = 179
    TC_3d_PktPkt_WinkelSeg_TE = 180
    TC_3d_PktPkt_AnzSims = 181
    TC_3d_PktPkt_Dia_BE = 182
    TC_3d_PktPkt_Dia_TE = 183
    TC_3d_KMG_AmpX = 184
    TC_3d_KMG_AmpY = 185

    def add_by_value(self, value: int):
        try:
            konst = TKompConstants(value)  # Enum-Zugriff über den Wert (int)
            return konst
        except ValueError:
            print(f"Ungültiger Wert: {value} ist kein gültiger TKompConstants-Eintrag")

    def add_by_name(self, name: str):
        try:
            # Enum-Zugriff über den Namen (string)
            konst = TKompConstants[name]
            return konst
        except KeyError:
            print(f"Ungültiger Name: {name} ist kein gültiger TKompConstants-Eintrag")


class TMU_ConstList(BaseModel):
    const_map: dict[TKompConstants, float] = {}

    @field_validator("const_map", mode="before")
    @classmethod
    def parse_const_map(cls, v):
        # Falls Keys als Strings ankommen
        if isinstance(v, dict):
            new_map = {}
            for k, val in v.items():
                if isinstance(k, str):
                    try:
                        enum_key = TKompConstants[k]
                    except KeyError:
                        raise ValueError(f"Ungültiger Schlüssel: {k}")
                else:
                    enum_key = k
                new_map[enum_key] = float(val)
            return new_map
        raise ValueError("const_map muss ein Dictionary sein")

    async def load_constants(self, anamu_id: int, db: AsyncSession):
        print("reached it")
        stmt = select(ANAKONST).where(ANAKONST.fk_anamu == anamu_id)
        result = await db.execute(stmt)
        constants = result.scalars().all()  # GIBT MODELLE, keine Tupel

        for const in constants:
            try:
                enum_key = TKompConstants(const.constnum)
                self.const_map[enum_key] = const.constval
            except ValueError:
                print(f"Unbekannter constnum {const.constnum} → nicht im Enum enthalten")

    class Config:
        use_enum_values = False
        json_encoders = {TKompConstants: lambda v: v.name}
