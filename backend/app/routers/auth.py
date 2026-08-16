import os
import secrets
import uuid
from datetime import timedelta, datetime
from typing import Annotated

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from fastapi import APIRouter, Depends, HTTPException, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import JSONResponse

from app.database.database import get_db
from app.models import RefreshToken
from app.models.LoginAttempts import LoginAttempt
from app.models.company import Company
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"

if os.path.exists(PRIVATE_KEY_FILE):
    with open(PRIVATE_KEY_FILE, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
else:
    # neues Schlüsselpaar generieren
    private_key = ed25519.Ed25519PrivateKey.generate()
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key_pem)

# Public Key genauso behandeln
if os.path.exists(PUBLIC_KEY_FILE):
    with open(PUBLIC_KEY_FILE, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
else:
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_key_pem)

SECRET_KEY = 'soll noch in EdDSA gemacht werden'
ALGORITHM = 'EdDSA'
MAX_LOGIN_ATTEMPTS = 5  # Maximale Anmeldeversuche
LOCKOUT_TIME = timedelta(minutes=15)  # Sperrzeit bei zu vielen Fehlversuchen

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/")
async def create_user(db: db_dependency, user_in: CreateUserRequest):
    create_user_model = User(username=user_in.username,
                              hashed_password=bcrypt_context.hash(user_in.password), role=user_in.role)
    db.add(create_user_model)
    await db.commit()
    return {"id": create_user_model.id}
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/token", response_model=Token)
async def login_for_access_token(login_request: LoginRequest,
    db: db_dependency, request: Request
):
    # Verwende login_request.username und login_request.password
    ip_address = request.client.host
    result = await db.execute(select(LoginAttempt).where(LoginAttempt.ip_address == ip_address))
    login_attempt = result.scalars().first()

    if login_attempt:
        if login_attempt.attempts >= MAX_LOGIN_ATTEMPTS and datetime.utcnow() - login_attempt.last_attempt < LOCKOUT_TIME:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                detail="Too many login attempts. Please try again later.")

    user = await authenticate_user(login_request.username, login_request.password, db)
    if not user:
        if login_attempt:
            login_attempt.attempts += 1
            login_attempt.last_attempt = datetime.utcnow()
        else:
            login_attempt = LoginAttempt(ip_address=ip_address, attempts=1)
            db.add(login_attempt)

        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    if login_attempt:
        login_attempt.attempts = 0
        await db.commit()

    token = create_access_token(user.username, user.id, timedelta(minutes=1))

    refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=7)

    # Store refresh token in DB
    new_token = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
    db.add(new_token)
    await db.commit()

    response = JSONResponse(content={"message": "Login successful"})

    # Access Token als HttpOnly-Cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # ⛔ Bei Entwicklung lokal False, im Livebetrieb auf True stellen!
        samesite="Lax",
        max_age=3600  # 5 Minuten
        ,path = "/"
    )

    # Refresh Token als HttpOnly-Cookie (optional)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7  # 7 Tage
        , path="/"

    )

    return response

async def authenticate_user(username: str, password: str, db):
    stmt = select(User).filter(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub':username, 'id': user_id, 'iat': datetime.utcnow()}
    expire = datetime.utcnow() + expires_delta
    encode.update({'exp': expire, 'jti': str(uuid.uuid4())})
    return jwt.encode(encode, private_key, algorithm=ALGORITHM)


from fastapi import Request


async def get_current_user(request: Request, db: db_dependency):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found in cookies.")

    try:
        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key_pem = f.read()

        # Entschlüsselung des Tokens
        payload = jwt.decode(token, public_key_pem, algorithms=[ALGORITHM])

        username: str = payload.get('sub')
        user_id: int = payload['id']

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

        # Überprüfe den Benutzer in der DB
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

@router.get("/me")
async def user(user: Annotated[dict, Depends(get_current_user)], db: db_dependency):
    if user is None:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail='Authentication failed.')
    return {"User": user}

@router.get("/refresh_token")
async def refresh_token(
    db: db_dependency,
    refresh_token: str = Cookie(),  # Cookie auslesen
):
    print("LEE",refresh_token)
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    print("TokenRE", refresh_token)

    token_entry = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    token_entry = token_entry.scalars().first()
    print("verdammte", token_entry)
    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    print("verdammt")

    user = await db.execute(select(User).where(User.id == token_entry.user_id))
    user = user.scalars().first()

    # Delete old refresh token
    await db.delete(token_entry)
    await db.commit()

    # Generate new refresh token
    new_refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=7)
    new_token_entry = RefreshToken(user_id=user.id, token=new_refresh_token, expires_at=expires_at)
    db.add(new_token_entry)
    await db.commit()

    # Generate access token
    new_access_token = create_access_token(user.username, user.id, timedelta(minutes=1))

    # Create response
    response = JSONResponse(content={"message": "Token refreshed"})

    # Set tokens as cookies on the actual JSONResponse object
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60
        , path="/"

    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7
        , path="/"

    )
    print(response.headers.getlist('set-cookie'))
    return response
@router.get("/refresh_tokens")
async def refresh_token(
    db: db_dependency,
    refresh_token: str = Cookie(),  # Cookie auslesen
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    print("TokenRE", refresh_token)

    token_entry = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    token_entry = token_entry.scalars().first()

    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = await db.execute(select(User).where(User.id == token_entry.user_id))
    user = user.scalars().first()

    # Delete old refresh token
    await db.delete(token_entry)
    await db.commit()

    # Generate new refresh token
    new_refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=7)
    new_token_entry = RefreshToken(user_id=user.id, token=new_refresh_token, expires_at=expires_at)
    db.add(new_token_entry)
    await db.commit()

    # Generate access token
    new_access_token = create_access_token(user.username, user.id, timedelta(minutes=1))

    # Create response
    response = JSONResponse(content={"message": "Token refreshed"})

    # Set tokens as cookies on the actual JSONResponse object
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60,
        path = "/"
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
        path = "/"
    )
    print(response.headers.getlist('set-cookie'))
    return response
@router.post("/logout")
async def logout(refresh_token: str, db: db_dependency):
    token_entry = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    token_entry = token_entry.scalars().first()
    if token_entry:
        await db.delete(token_entry)
        await db.commit()

    return {"message": "Logged out"}

def require_roles(*allowed_roles: str):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return role_checker


@router.get("/edit")
async def editor_or_admin(user: User = Depends(require_roles("editor", "admin"))):
    return {"message": f"Hallo {user.username}, du hast Bearbeitungsrechte!"}

@router.get("/admin", response_model=bool)
async def has_edit_permission(user: User = Depends(get_current_user)):
    return user.role in {"editor", "admin"}

@router.post("/create_user")
async def create_user_for_company(user_in: CreateUserRequest, db: db_dependency,
                                  current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create users.")

    company = await db.execute(select(Company).where(Company.id == current_user.company_id))
    company = company.scalars().first()

    new_user = User(
        username=user_in.username,
        hashed_password=bcrypt_context.hash(user_in.password),
        role=user_in.role,
        company_id=company.id
    )
    db.add(new_user)
    await db.commit()
    return {"id": new_user.id}

@router.get("/company_data")
async def get_company_data(db: db_dependency, current_user: User = Depends(get_current_user)):
    result = await db.execute(select(User).where(User.fk_company == current_user.fk_company))
    data = result.scalars().all()
    return data

