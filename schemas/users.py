from pydantic import BaseModel, EmailStr, Field
from models.users import TypeUser

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    type: TypeUser

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    type: TypeUser
    active: bool

    class Config:
        from_attributes = True