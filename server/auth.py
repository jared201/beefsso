from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_users.authentication import JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pydantic import BaseModel
import pyotp

DATABASE_URL = "sqlite:///./test.db"
SECRET = "SECRET"

Base: DeclarativeMeta = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    # Define your user model here
    pass

class UserCreate(BaseModel):
    # Define your user creation model here
    pass

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
        # Generate OTP and send to user
        totp = pyotp.TOTP(user.otp_secret)
        # Send OTP to user via email/SMS
        return {"otp_required": True}
    return {"error": "Invalid credentials"}

@app.post("/auth/jwt/verify-otp")
async def verify_otp(otp: str, user: User = Depends(fastapi_users.get_current_active_user)):
    totp = pyotp.TOTP(user.otp_secret)
    if totp.verify(otp):
        return await fastapi_users.get_auth_backend().get_login_response(user, None)
    return {"error": "Invalid OTP"}

fastapi_users.create_user_router()
fastapi_users.create_auth_router(auth_backend)