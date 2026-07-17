from sqlalchemy import Column, Integer, String, Boolean, Enum
from database import Base
import enum
from sqlalchemy.orm import relationship

class TypeUser(enum.Enum):
    client = "client"
    seller = "seller"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    type = Column(Enum(TypeUser), nullable=False)
    active = Column(Boolean, default=True)

    charts = relationship("Chart", back_populates="user")
    books = relationship("Item", back_populates="seller") 