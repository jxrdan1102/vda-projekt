from app.database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(String(8), default="user")
    fk_company = Column(Integer, ForeignKey("companies.id"))

    company = relationship("Company", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user")
    modells = relationship("Modell", back_populates="owner")
    anamu = relationship("ANAMU", back_populates="user")

