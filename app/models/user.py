from sqlalchemy import String, Enum, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum

class RoleEnum(str, enum.Enum):
    doctor = "doctor"
    nurse = "nurse"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("length(trim(full_name)) > 0", name="non_empty_full_name"),
        CheckConstraint("length(trim(email)) > 0", name="non_empty_email"),
        CheckConstraint("length(hashed_password) > 0", name="non_empty_hashed_password"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)

    patients = relationship("Patient", back_populates="creator")

    consultations = relationship("Consultation", back_populates="doctor") 