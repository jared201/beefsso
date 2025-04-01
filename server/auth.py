from fastapi import FastAPI, Depends, HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String
from pydantic import BaseModel
import pyotp

DATABASE_URL = "sqlite:///./test.db"
SECRET = "SECRET"

Base: DeclarativeMeta = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    otp_secret = Column(String, nullable=False)

class UserCreate(BaseModel):
    email: str
    password: str

class UserUpdate(UserCreate):
    pass

class UserDB(User, UserCreate):
    pass

user_db = SQLAlchemyUserDatabase(UserDB, SessionLocal, User)

jwt_strategy = JWTStrategy(secret=SECRET, lifetime_seconds=3600)
auth_backend = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")

fastapi_users = FastAPIUsers(
    user_db,
    [auth_backend],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

app = FastAPI()

@app.post("/auth/jwt/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await fastapi_users.authenticate(form_data)
    if user:
        totp = pyotp.TOTP(user.otp_secret)
        # Send OTP to user via email/SMS
        return {"otp_required": True}
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.post("/auth/jwt/verify-otp")
async def verify_otp(otp: str, user: User = Depends(fastapi_users.get_current_active_user)):
    totp = pyotp.TOTP(user.otp_secret)
    if totp.verify(otp):
        return await fastapi_users.get_auth_backend().get_login_response(user, None)
    raise HTTPException(status_code=400, detail="Invalid OTP")

fastapi_users.create_user_router()
fastapi_users.create_auth_router(auth_backend)