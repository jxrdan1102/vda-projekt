from sqlalchemy import Column, Integer, String
from app.database.database import Base

class ModellText(Base):
    __tablename__ = "modell_texts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deutsch = Column(String(500), nullable=True)
    englisch = Column(String(500), nullable=True)
    spanisch = Column(String(500), nullable=True)
    french = Column(String(500), nullable=True)
    italian = Column(String(500), nullable=True)