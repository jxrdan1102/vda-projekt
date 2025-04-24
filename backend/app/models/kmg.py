from app.database.database import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship


class KMG(Base):
    __tablename__ = "kmgs"

    id = Column(Integer, primary_key=True, index=True)
    kmg_ident = Column(Integer, index=True)
    kmg_bez = Column(String(255))
    kmg_a = Column(Float)
    kmg_k = Column(Float)
    kmg_lt = Column(Float)
    kmg_uc = Column(Float)
    kmg_alpham = Column(Float)
    kmg_mpeml = Column(Float)

    anamu = relationship("ANAMU", back_populates="kmg")
