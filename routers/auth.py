from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from models.users import User, TypeUser
from schemas.users import UserCreate, UserResponse
from auth import password_hash, verify_password, create_token
from dependencies import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["auth"])


# JSON LOGIN SCHEMA
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# REGISTER
@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(data: UserCreate, db: Session = Depends(get_db)):
    existent_user = db.query(User).filter(User.email == data.email).first()
    if existent_user:
        raise HTTPException(status_code=400, detail="Email is already in use")

    new_user = User(
        name=data.name,
        email=data.email,
        password_hash=password_hash(data.password),
        type=data.type
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# form data login (SWAGGER'S MANDATORY)
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # OAuth2PasswordRequestForm uses 'username', but our database uses 'email'
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="incorrect password or email")

    token = create_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# json login for tests
@router.post("/login-json")
def login_json(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="incorrect password or email")

    token = create_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# get current user info (used by client to auto-detect user type)
@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Return current logged-in user information including type (client/seller)."""
    return current_user