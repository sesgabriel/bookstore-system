from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# Hashing config
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT config
SECRET_KEY = "troque-essa-chave-por-algo-bem-aleatorio"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(pure_password: str, password_hash: str) -> bool:
    return pwd_context.verify(pure_password, password_hash)


def create_token(data: dict) -> str:
    data_to_codify = data.copy()
    expires_in = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data_to_codify.update({"exp": expires_in})
    token = jwt.encode(data_to_codify, SECRET_KEY, algorithm=ALGORITHM)
    return token