# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 12:06:21 2023

@author: Uwe
"""

import numpy as np
import numpy.linalg as la
from numpy.random import default_rng

rng = default_rng(42)
# from scipy import optimize

standalone = 0


# We can simplify it with a new class
class TProperties:
    def __init__(Self, DelphiVar):
        Self.__DelphiVar__ = DelphiVar

    def __getattr__(Self, Key):
        return Self.__dict__['__DelphiVar__'].Value[Key]

    def __setattr__(Self, Key, Value):
        if Key == "__DelphiVar__":
            Self.__dict__['__DelphiVar__'] = Value
        else:
            Self.__DelphiVar__.Value[Key] = Value
            Self.__DelphiVar__.Value = Self.__DelphiVar__.Value

    def __repr__(Self):
        return str(Self.__DelphiVar__.Value)

    def __str__(Self):
        return str(Self.__DelphiVar__.Value)


nur_rechnen = 0
num_bins = 20  # Anzahl Klassen fest? => EL fragen !!!
num_sims = 100  # Vorbelegung Anzahl Simulationen
kmg_ampx = 0.0  # Vorbelegung Streuung Amplitude coord_x mm (KMG)
kmg_ampy = 0.0  # Vorbelegung Streuung Amplitude coord_y mm (KMG)


class Punkt:
    coord_x = 0
    coord_y = 0

    def __init__(self, x=0.0, y=0.0):  # constructor
        self.coord_x = x
        self.coord_y = y
        self.punkt_wolke = np.empty(shape=(num_sims, 2))

    def wolke_erzeugen(self):
        self.punkt_wolke = rng.standard_normal(size=(num_sims, 2))
        for i in range(num_sims):
            self.punkt_wolke[i, 0] = self.coord_x + kmg_ampx / 3. * self.punkt_wolke[i, 0]
            self.punkt_wolke[i, 1] = self.coord_y + kmg_ampy / 3. * self.punkt_wolke[i, 1]


class Kreis(Punkt):
    """ Kreis Objekt """
    # coord_x=0
    # coord_y=0
    dia = 0
    anz_punkte = 0
    k_segment = 360
    Schrittwinkel = 0.0

    def __init__(self, midx=0.0, midy=0.0, dia=0.0, numpoints=8, segment=360):  # constructor
        super().__init__(midx, midy)  # initialisierung Punkt()
        # self.coord_x = midx
        # self.coord_y = midy
        self.dia = dia
        self.anz_punkte = numpoints
        self.k_segment = segment
        self.ideal = np.empty(shape=(self.anz_punkte, 2))  # np.empty([8,2], dtype = float )
        self.calc()  # idealkreis mit diesen Parametern erzeugen
        self.wolke_erzeugen()  # Montecarlo Simulation:  Kreismittelpunkte erzeugen

    def calc(self):
        """ Kreisberechnung Idealkreis """
        self.schrittwinkel = (self.k_segment * np.pi / 180) / self.anz_punkte
        for i in range(0, self.anz_punkte):
            self.ideal[i, 0] = self.coord_x + self.dia / 2 * np.cos(i * self.schrittwinkel)
            self.ideal[i, 1] = self.coord_y + self.dia / 2 * np.sin(i * self.schrittwinkel)

    """ ------------------------------------------------------------------------
      Kreisberechnung Ausgleichskreis mit scipy

    def calc_ausgleichskreisA(self, points ):
        x = points[:,0] # Split x and y coordinates
        y = points[:,1]
        x_m = np.mean(x)  # coordinates of the barycenter
        y_m = np.mean(y)
        def calc_R(xc, yc):
            " "" calculate the distance of each 2D points from the center (xc, yc) "" "
            return np.sqrt((x-xc)**2 + (y-yc)**2)
        # @countcalls
        def f_2(c):
            " "" calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) "" "
            Ri = calc_R(*c)
            return Ri - Ri.mean()
        center_estimate = x_m, y_m
        " "" kleinste Quadrate für Ausgleichskreis "" "
        center_2, ier = optimize.leastsq(f_2, center_estimate)
        xc_2, yc_2 = center_2
        return xc_2, yc_2          # radius?
   ------------------------------------------------------------------------------  """

    def calc_ausgleichskreis(self, points):
        xk = points[:, 0]  # x und y herauslösen
        yk = points[:, 1]

        # Finde Kreisgleichung
        A = np.column_stack((2. * xk, 2 * yk, np.ones_like(xk)))
        rhs = xk * xk + yk * yk
        # Berechne Lösung des Ausgleichsproblem
        a, b, c = la.lstsq(A, rhs, rcond=-1)[0]
        # r = np.sqrt(c+a**2+b**2) r=Radius: wird nicht benötigt
        # xc_2, yc_2 = a, b
        return a, b  # Mittelpunkt des Ausgleichskreises

    def wolke_erzeugen(self):
        """ Koordinaten des Idealkreises zufällig verändern, Ergebnis in zufall """
        zufall = np.empty(shape=(self.anz_punkte, 2))
        for s in range(num_sims):
            zufall = rng.standard_normal(size=(self.anz_punkte, 2))
            for i in range(self.anz_punkte):  # zufällige Punkte um die Idealpunkte berechnen
                # idx=s*self.anz_punkte + i # Zielindex in zufall
                zufall[i, 0] = self.ideal[i][0] + kmg_ampx / 3. * zufall[i, 0]  # x(i) + zufall
                zufall[i, 1] = self.ideal[i][1] + kmg_ampy / 3. * zufall[i, 1]  # y(i) + zufall
            self.punkt_wolke[s] = self.calc_ausgleichskreis(zufall)  # Punktwolke um Kreismittelpunkt


# ----------------------------------------------------------------------------

def calc_abstand(KreisA, KreisB):
    dist_ideal = np.sqrt((KreisA.coord_x - KreisB.coord_x) ** 2 + (KreisA.coord_y - KreisB.coord_y) ** 2)
    dist = np.sqrt((KreisA.punkt_wolke[:, 0] - KreisB.punkt_wolke[:, 0]) ** 2 + (
                KreisA.punkt_wolke[:, 1] - KreisB.punkt_wolke[:, 1]) ** 2) - dist_ideal
    return dist


def verteilung(dist, f):
    model = np.poly1d(np.polyfit(dist[:, 0], dist[:, 1], deg=3))
    xx3, xx2, xx1, xx0 = model
    # ApproxZufWert Konfidenz(D9:D14) bzw. D93:D98
    dist[:, 2] = xx3 * pow(dist[:, 0], 3) + xx2 * pow(dist[:, 0], 2) + xx1 * dist[:, 0] + xx0

    # Konfidenz Intervall G10 F
    # f_oeg=0.975 # G94 konstant
    intervall = xx3 * pow(f, 3) + xx2 * pow(f, 2) + xx1 * f + xx0  # G95 a1,a2,a3,a4
    return intervall


def mu_position(elementA, elementB, AnzSims, KMG_AmpX, KMG_AmpY ):
    d = calc_abstand(elementA, elementB)  # d als array der Mittelpunktabstände der simulierten Kreise
    global num_sims, kmg_ampx, kmg_ampy  # hier sagst du Python, dass du die globalen Variablen meinst
    num_sims = AnzSims
    kmg_ampx = KMG_AmpX
    kmg_ampy = KMG_AmpY
    xbar = np.mean(d)
    vstd = np.std(d)

    with open(r"C:\Users\Jason\test.txt", "w", encoding="utf-8") as f:
        # Attribute von elementA
        f.write(f"ElementA:\n")
        f.write(f"  coord_x: {elementA.coord_x}\n")
        f.write(f"  coord_y: {elementA.coord_y}\n")
        if isinstance(elementA, Kreis):
            f.write(f"  dia: {elementA.dia}\n")
            f.write(f"  anz_punkte: {elementA.anz_punkte}\n")
        f.write("\n")

        # Attribute von elementB
        f.write(f"ElementB:\n")
        f.write(f"  coord_x: {elementB.coord_x}\n")
        f.write(f"  coord_y: {elementB.coord_y}\n")
        if isinstance(elementB, Kreis):
            f.write(f"  dia: {elementB.dia}\n")
            f.write(f"  anz_punkte: {elementB.anz_punkte}\n")
        f.write("\n")

        # Statistiken
        f.write(f"Anzahl Simulationen je Messpunkt      {num_sims}\n")
        f.write(f"Anzahl Klassen  (fix?)                {num_bins}\n")
        f.write(f"Mittelwert(delta d(i))           {xbar:8.7f}\n")
        f.write(f"Standardabweichung( delta d(i) ) {vstd:8.7f}\n")
        f.write("\n")

        # Einzelne Abstände ausgeben
        f.write("Einzelne Abstände d[i]:\n")
        for i, val in enumerate(d):
            f.write(f"  d[{i}] = {val:8.7f}\n")

    # su berechnen
    dens, densbins = np.histogram(d, num_bins, density=True)

    # siehe auch Integral_Funk EL  MIT Klassen
    H, X1 = np.histogram(d, bins=num_bins, density=True)
    bin_breite = X1[1] - X1[0]
    F1 = np.cumsum(H) * bin_breite

    # Klassenmitten berechnen (statt densbins)
    bin_centers = (X1[:-1] + X1[1:]) / 2

    vert_oeg = np.empty(shape=(6, 3))
    vert_ueg = np.empty(shape=(6, 3))

    # Datei vorbereiten
    log_file = r"C:\Users\Jason\testss.txt"
    with open(log_file, "w", encoding="utf-8") as f:

        f.write("=== DEBUG LOG: mu_position ===\n\n")

        # --- Basisdaten ---
        f.write(f"num_bins = {num_bins}\n")
        f.write(f"num_sims = {num_sims}\n")
        f.write(f"bin_breite = {bin_breite}\n\n")

        f.write("Histogramm H (density=True):\n")
        f.write(np.array2string(H, precision=6, separator=", ") + "\n\n")

        f.write("X1 (Klassengrenzen):\n")
        f.write(np.array2string(X1, precision=6, separator=", ") + "\n\n")

        f.write("bin_centers (Klassenmitten):\n")
        f.write(np.array2string(bin_centers, precision=6, separator=", ") + "\n\n")

        f.write("F1 (kumulative Summe):\n")
        f.write(np.array2string(F1, precision=6, separator=", ") + "\n\n")

        # ------------------------------------------ OEG -----------------------
        ix = 0
        for i in range(num_bins - 7, num_bins - 1):
            vert_oeg[ix, 0] = F1[i]
            vert_oeg[ix, 1] = bin_centers[i]  # <- hier besser als densbins
            ix += 1

        f.write("vert_oeg (x=F1, y=bin_centers):\n")
        f.write(np.array2string(vert_oeg, precision=6, separator=", ") + "\n\n")

        oeg_intervall = verteilung(vert_oeg, 0.975)
        f.write(f"oeg_intervall = {oeg_intervall}\n\n")

        # ----------------------------------------- UEG -----------------------
        ix = 0
        for i in range(3, 9):
            vert_ueg[ix, 0] = F1[i]
            vert_ueg[ix, 1] = bin_centers[i]
            ix += 1

        f.write("vert_ueg (x=F1, y=bin_centers):\n")
        f.write(np.array2string(vert_ueg, precision=6, separator=", ") + "\n\n")

        ueg_intervall = verteilung(vert_ueg, 0.025)
        f.write(f"ueg_intervall = {ueg_intervall}\n\n")

        # ------------------------------ Finale -------------------------------
        konfi95 = oeg_intervall - ueg_intervall
        su = konfi95 / 2

        f.write(f"Konfidenzintervall (95%) = {konfi95}\n")
        f.write(f"SU = {su}\n")
    with open(r"C:\Users\Jason\tests.txt", "w", encoding="utf-8") as f:

        f.write(f"OG_Intervall               %8.5f" % (oeg_intervall))
        f.write(f"UG_Intervall               %8.5f" % (ueg_intervall))

        f.write(f"Konfidenzintervall (95°/.) %8.5f mm" % (konfi95))
        f.write(f"xbar = {xbar}\n")
        f.write(f"vstd = {vstd}\n")
        f.write(f"SU = {su}\n")
    return xbar, vstd, su


# main
print("Standalone=", standalone)

if (standalone == 0):  # hier kommen die Daten von Delphi
    print()
else:
    num_sims = 5000  # Anzahl Simulationen
    kmg_ampx = 0.0005  # Streuung Amplitude coord_x mm (KMG)
    kmg_ampy = 0.0005  # Streuung Amplitude coord_y mm (KMG)
    element1 = Kreis(midx=0, midy=0, dia=50, numpoints=8, segment=350)
    element2 = Kreis(midx=50, midy=0, dia=50, numpoints=8, segment=350)
    print("-----------------------------------------------------")
    print("Kreis - Kreis")
    mu_position(element1, element2)
