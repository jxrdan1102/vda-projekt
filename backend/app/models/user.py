from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(8), default="user")
    fk_company = Column(Integer, ForeignKey("companies.id"))

    components = relationship("Component", back_populates="user")
    company = relationship("Company", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    modells = relationship("Modell", back_populates="owner")
    anamu = relationship("ANAMU", back_populates="user")
    anakomp = relationship("ANAKOMP", back_populates="user")
    anakonst = relationship("ANAKONST", back_populates="user")
    fk_company = Column(Integer, ForeignKey("companies.id"), nullable=True)


