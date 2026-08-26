from sqlalchemy import DATETIME, Column, ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship

from app.database.database import Base


class KMG(Base):
    __tablename__ = "kmgs"

    id = Column(Integer, primary_key=True, index=True)
    kmg_ident = Column(String(255), index=True)
    kmg_bez = Column(String(255))
    kmg_a = Column(Float)
    kmg_k = Column(Float)
    kmg_lt = Column(Float)
    kmg_uc = Column(Float)
    kmg_alpham = Column(Float)
    kmg_mpeml = Column(Float)

    fk_user_id = Column(Integer, ForeignKey("users.id"))
    fk_company = Column(Integer, ForeignKey("companies.id"), nullable=True)
    anamu = relationship("ANAMU", back_populates="kmg")
