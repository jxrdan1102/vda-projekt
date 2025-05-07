from app.database.database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)

    users = relationship("User", back_populates="company")