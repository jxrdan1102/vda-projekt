class KMGAdmin:
    def __init__(self, data, CMM=""):
        self.CMM = CMM
        self.current_index = 0
        self.KMG_IDENT = data.KMG_IDENT
        self.KMG_BEZ = data.KMG_BEZ
        self.KMG_A = data.KMG_A
        self.KMG_K = data.KMG_K
        self.KMG_LT = data.KMG_LT
        self.KMG_UC = data.KMG_UC
        self.KMG_ALPHAM = data.KMG_ALPHAM

    @property
    def berechne_MPEML(self):
        if self.KMG_K is None or self.KMG_K == 0 or self.KMG_LT is None:
            return None
        return 4 * (self.KMG_LT / self.KMG_K)
