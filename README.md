## BeefSSO

BeefSSO is a Single Sign-On (SSO) solution for web applications that allows users to authenticate once and gain access to multiple applications without needing to log in again. It is designed to be easy to use and integrate with existing applications.

## Current problems with existing solutions

Here is a table listing some common problems with existing Single Sign-On (SSO) solutions:

| Problem                         | Description                                                                   |
|---------------------------------|-------------------------------------------------------------------------------|
| Complexity                      | Many SSO solutions are complex to set up and configure.                       |
| Vendor Lock-in                  | Some solutions tie you to a specific vendor, limiting flexibility.            |
| Security Risks                  | Centralized authentication can be a single point of failure if compromised.   |
| Scalability Issues              | Not all SSO solutions scale well with increasing number of users.             |
| Integration Challenges          | Integrating SSO with existing applications can be difficult.                  |
| User Experience                 | Poorly implemented SSO can lead to a confusing user experience.               |
| Cost                            | Enterprise-level SSO solutions can be expensive.                              |
| Maintenance Overhead            | Regular updates and maintenance are required to keep the system secure.       |
| Limited Customization           | Some solutions offer limited options for customization to fit specific needs. |
| Compliance and Privacy Concerns | Ensuring compliance with privacy regulations can be challenging.              |

## Features

- **Easy Integration**: BeefSSO is designed to be easy to integrate with existing applications, regardless of the technology stack.
- **User-Friendly**: The user interface is intuitive and easy to use, making it simple for users to log in and access their applications.

- **Secure**: BeefSSO uses industry-standard security protocols to ensure that user data is protected.
- **Scalable**: BeefSSO is designed to scale with your organization, allowing you to add new applications and users as needed.

- **Customizable**: BeefSSO can be customized to fit your organization's specific needs, including branding and user experience.
- **Open Source**: BeefSSO is open source, allowing you to modify and extend the code to fit your needs.

## Uses FastAPI

BeefSSO is built using FastAPI, a modern web framework for building APIs with Python. FastAPI is known for its high performance, ease of use, and automatic generation of OpenAPI documentation. By using FastAPI, BeefSSO can provide a fast and efficient authentication solution for web applications.

To create a robust SSO OAuth solution with Multi-Factor Authentication (MFA), you need several components:

1. **OAuth2 Provider**: Handles the OAuth2 authentication flow.
2. **User Management**: Manages user data and authentication states.
3. **MFA Integration**: Adds an additional layer of security by requiring a second form of authentication.
4. **Token Management**: Issues and validates tokens for authenticated sessions.
5. **API Endpoints**: Provides endpoints for login, token issuance, and user information.

Here is a basic implementation using FastAPI and `fastapi-users` for user management and OAuth2, along with `pyotp` for MFA.

### 1. Install Required Libraries

Add the following to your `requirements.txt`:

```
fastapi
uvicorn
fastapi-users[sqlalchemy2,oauth2]
pyotp
```

### 2. OAuth2 Provider and User Management

Create a file `auth.py`:

```python
from fastapi import FastAPI, Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import OAuth2PasswordBearer, OAuth2PasswordRequestForm, JWTStrategy
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
async def verify_otp(user: User = Depends(fastapi_users.get_current_active_user), otp: str):
    totp = pyotp.TOTP(user.otp_secret)
    if totp.verify(otp):
        return await fastapi_users.get_auth_backend().get_login_response(user, None)
    return {"error": "Invalid OTP"}

fastapi_users.create_user_router()
fastapi_users.create_auth_router(auth_backend)
```

### 3. Main Server Module

Update your `server/server.py`:

```python
from fastapi import FastAPI
from auth import app as auth_app

app = FastAPI()

app.mount("/auth", auth_app)

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

This setup provides a basic structure for an SSO OAuth solution with MFA. You will need to implement the user model, user creation, and OTP sending logic according to your specific requirements.

## Installation

## Run the following command to install the required dependencies:

```bash
pip install -r requirements.txt
```
## Run the application

```bash   
uvicorn server.server:app --reload
```
