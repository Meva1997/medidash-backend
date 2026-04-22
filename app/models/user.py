from sqlalchemy import Column, Integer, String, Enum
from app.database import Base
import enum 

#RoleEnum is an enumeration that defines the possible roles for a user in the system. 
class RoleEnum(str, enum.Enum):
    doctor = "doctor"
    nurse = "nurse"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)