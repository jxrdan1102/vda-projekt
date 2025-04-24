from app.database.database import Base
from sqlalchemy import DATETIME, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class ANAMU(Base):
    __tablename__ = "ana_mu"

    id = Column(Integer, primary_key=True)
    fk_modell = Column(Integer, ForeignKey("modells.id"), index=True)
    name = Column(String(255))
    aenderungszustand = Column(String(15))
    identnr = Column(Integer)
    partno = Column(Integer)
    remark = Column(String(255))
    creation = Column(DATETIME)
    modify = Column(DATETIME)
    user = Column(Integer)
    tolfaktor = Column(Integer)
    tsk_aufgabe = Column(Integer)
    fk_kmg = Column(Integer, ForeignKey("kmgs.id"))

    kmg = relationship("kmgs", backref="anamu")
    modell = relationship("Modell", back_populates="ana_mu")
    anakomp = relationship("ANAKOMP", back_populates="anamu")


class ANAKONST(Base):
    __tablename__ = "anakonst"

    id = Column(Integer, primary_key=True)
    fk_anamu = Column(Integer)
    constnum = Column(Integer)
    constval = Column(Float)
    remark = Column(String(255))


class ANAKOMP(Base):
    __tablename__ = "anakomp"

    id = Column(Integer, primary_key=True)
    fk_anamu = Column(Integer, ForeignKey("ana_mu.id"))
    fk_mod_components = Column(Integer, ForeignKey("mod_components.id"))
    remark = Column(String(255))
    terml0 = Column(Float)
    terml1 = Column(Float)
    wertart = Column(Integer)
    freigrad = Column(Integer)
    frei_n_1 = Column(Integer)
    verteilung = Column(Integer)

    komponente = relationship("Component", back_populates="anakomp")
    anamu = relationship("ANAMU", back_populates="anakomp")
