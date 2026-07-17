from pydantic import BaseModel, Field
from typing import Optional

class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    author: Optional[str] = Field(None, max_length=200)
    price: float = Field(..., ge=0, description="Price must be non-negative")
    stock: int = Field(..., ge=0, description="Stock must be non-negative")

class ItemCreate(ItemBase):
    pass  # data to create

class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True  # convert model SQLAlchemy → Pydantic

class ItemUpdate(BaseModel):
    """All fields optional for partial updates."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=1000)
    author: Optional[str] = Field(None, max_length=200)
    price: Optional[float] = Field(None, ge=0, description="Price must be non-negative")
    stock: Optional[int] = Field(None, ge=0, description="Stock must be non-negative")