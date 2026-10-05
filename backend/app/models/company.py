from sqlalchemy import Boolean, Column, Integer, String, true
from sqlalchemy.orm import relationship

from app.database.database import Base


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default=true())

    users = relationship("User", back_populates="company")
