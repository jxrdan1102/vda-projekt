from app.database.database import Base
from sqlalchemy import DATETIME, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Modell(Base):
    __tablename__ = "modells"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), index=True)
    description = Column(String(512))
    geo_me = Column(Integer)
    geo_mo = Column(Integer)
    geo_gn = Column(Integer)
    geo_bn = Column(Integer)
    tol_fak = Column(Integer)
    aufgabe = Column(Integer)
    methode = Column(Integer)
    gegenstanf = Column(Integer)
    messeinsatz = Column(Integer)
    einstellmass = Column(Integer)
    modcreation = Column(DATETIME)
    modmod = Column(DATETIME)
    tsk_ausenmessung = Column(Integer)
    tsk_innenmessung = Column(Integer)
    tsk_tiefenmessung = Column(Integer)
    tsk_hoehenmessung = Column(Integer)
    tsk_stufenmessung = Column(Integer)
    formel = Column(String(512))
    formeldesc = Column(String(512))

    fk_user_id = Column(Integer, ForeignKey("users.id"))  # 🔐 Ownership
    owner = relationship(
        "User", back_populates="modells"
    )  # Optional für Zugriff von der anderen Seite
    components = relationship("Component", back_populates="modell")
    ana_mu = relationship("ANAMU", back_populates="modell")
