from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Drug(Base):
    __tablename__ = "drugs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    interactions = Column(Text, nullable=True)