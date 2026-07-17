from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    author = Column(String, index=True, nullable=True)
    price = Column(Numeric, nullable=False, default=0)
    stock = Column(Integer, index=True, default=0)
    description = Column(String)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False) 

    seller = relationship("User", back_populates="books")

    # ensure non-negative values at database level
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_non_negative"),
        CheckConstraint("stock >= 0", name="check_stock_non_negative"),
    )