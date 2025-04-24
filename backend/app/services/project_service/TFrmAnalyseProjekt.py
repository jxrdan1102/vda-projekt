class TFrmAnalyseProjekt:
    def __init__(self, analyse_id: int, aus_archiv: bool, modell: "TMU_Modell"):
        self.modell = modell
        self.analyse_id = analyse_id
        self.aus_archiv = aus_archiv

    def calculate(self):
        return self.modell.MUPruefverfahren_U()
