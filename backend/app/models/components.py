from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.database import Base


class Component(Base):
    __tablename__ = "mod_components"

    id = Column(Integer, primary_key=True)
    fk_modell = Column(Integer, ForeignKey("modells.id"), index=True)
    lfdnr = Column(Integer)
    kompid = Column(Integer)
    modltxtid = Column(Integer)
    terml0 = Column(Float)
    terml1 = Column(Float)
    wertart = Column(Integer)
    freigrad = Column(Integer)
    frei_n_1 = Column(Integer)
    verteilung = Column(Integer)
    kflags = Column(Integer)
    messpunkt_anzahl = Column(Integer, default = 0)
    anzahl_messungen = Column(Integer)
    fk_user_id = Column(Integer, ForeignKey("users.id"))

    fk_company = Column(Integer, ForeignKey("companies.id"), nullable=True)
    user = relationship("User", back_populates="components")
    modell = relationship("Modell", back_populates="components")
    anakomp = relationship("ANAKOMP", back_populates="komponente")
    fk_company = Column(Integer, ForeignKey("companies.id"), nullable=True)