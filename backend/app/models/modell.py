from sqlalchemy import DATETIME, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Modell(Base):
    __tablename__ = "modells"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True)
    description = Column(String(512))
    geo_me = Column(Integer)
    geo_mo = Column(Integer)
    aufgabe_modell = Column(Integer)
    geo_bn = Column(Integer)
    tol_fak = Column(Integer)
    aufgabe = Column(Integer)
    methode = Column(Integer)
    gegenstand = Column(Integer)
    messeinsatz = Column(Integer)
    einstellmass = Column(Integer)
    modcreation = Column(DATETIME)
    modmod = Column(DATETIME)
    tsk_ausenmessung = Column(Integer)
    tsk_innenmessung = Column(Integer)
    tsk_tiefenmessung = Column(Integer)
    tsk_hoehenmessung = Column(Integer)
    tsk_stufenmessung = Column(Integer)
    punktmuster = Column(Integer)
    Element1 = Column(String(255))
    Element2 = Column(String(255))
    Bezug1 = Column(String(255))
    Bezug2 = Column(String(255))
    winkelE1 = Column(Integer)
    winkelE2 = Column(Integer)
    winkelB1 = Column(Integer)
    winkelB2 = Column(Integer)
    taster = Column(Integer)
    merkmal = Column(Integer)
    element = Column(Integer)
    punktmusterB1 = Column(Integer)
    tasterschaft1 = Column(Integer, default=1)
    tasterschaft2 = Column(Integer, default=1)
    punktmusterR1 = Column(Integer)
    punktmusterR2 = Column(Integer)
    taster1 = Column(Integer)
    taster2 = Column(Integer)
    abstand = Column(Integer)

    formel = Column(String(512))
    formeldesc = Column(String(512))

    fk_user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="modells")
    components = relationship("Component", back_populates="modell")
    ana_mu = relationship("ANAMU", back_populates="modell")
