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

from app.core import roles
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

class Token(BaseModel):
    access_token: str
    token_type: str


db_dependency = Annotated[Session, Depends(get_db)]


class LoginRequest(BaseModel):
    username: str
    password: str


def _set_auth_cookies(response: JSONResponse, access_token: str, refresh_token: str, access_max_age: int) -> None:
    # ⛔ secure=False nur für die lokale Entwicklung, im Livebetrieb auf True stellen!
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False,
                        samesite="Lax", max_age=access_max_age, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False,
                        samesite="Lax", max_age=60 * 60 * 24 * 7, path="/")


async def _company_is_active(user: User, db) -> bool:
    """Superadmin hängt an keiner Firma. Bei allen anderen muss die Firma aktiv sein."""
    if user.role == roles.SUPERADMIN or user.fk_company is None:
        return True
    company = await db.get(Company, user.fk_company)
    return company is not None and bool(company.is_active)


async def _issue_refresh_token(user: User, db) -> str:
    refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=7)
    db.add(RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at))
    await db.commit()
    return refresh_token


@router.post("/token", response_model=Token)
async def login_for_access_token(login_request: LoginRequest,
    db: db_dependency, request: Request
):
    ip_address = request.client.host
    result = await db.execute(select(LoginAttempt).where(LoginAttempt.ip_address == ip_address))
    login_attempt = result.scalars().first()

    if login_attempt:
        if login_attempt.attempts >= MAX_LOGIN_ATTEMPTS and datetime.utcnow() - login_attempt.last_attempt < LOCKOUT_TIME:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                detail="Zu viele Anmeldeversuche. Bitte später erneut versuchen.")

    user = await authenticate_user(login_request.username, login_request.password, db)
    if not user:
        if login_attempt:
            login_attempt.attempts += 1
            login_attempt.last_attempt = datetime.utcnow()
        else:
            login_attempt = LoginAttempt(ip_address=ip_address, attempts=1)
            db.add(login_attempt)

        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Benutzername oder Passwort falsch")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Benutzer ist deaktiviert")
    if not await _company_is_active(user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Firma ist deaktiviert")

    if login_attempt:
        login_attempt.attempts = 0
        await db.commit()

    token = create_access_token(user, timedelta(minutes=1))
    refresh_token = await _issue_refresh_token(user, db)

    response = JSONResponse(content={"message": "Login successful"})
    _set_auth_cookies(response, token, refresh_token, access_max_age=3600)
    return response


async def authenticate_user(username: str, password: str, db):
    stmt = select(User).filter(User.username == username)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return False

    return user


def create_access_token(user: User, expires_delta: timedelta):
    encode = {
        'sub': user.username,
        'id': user.id,
        'role': user.role,
        'company': user.fk_company,
        'iat': datetime.utcnow(),
    }
    expire = datetime.utcnow() + expires_delta
    encode.update({'exp': expire, 'jti': str(uuid.uuid4())})
    return jwt.encode(encode, private_key, algorithm=ALGORITHM)


async def get_current_user(request: Request, db: db_dependency):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token not found in cookies.")

    try:
        with open(PUBLIC_KEY_FILE, "rb") as f:
            public_key_pem = f.read()

        payload = jwt.decode(token, public_key_pem, algorithms=[ALGORITHM])

        username: str = payload.get('sub')
        user_id: int = payload['id']

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

        # Rolle und Firma immer frisch aus der DB, nicht aus dem Token
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
        if not user.is_active or not await _company_is_active(user, db):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User deaktiviert')

        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')


def require_superadmin(current_user: User = Depends(get_current_user)):
    if current_user.role != roles.SUPERADMIN:
        raise HTTPException(status_code=403, detail="Nur Superadmin erlaubt")
    return current_user

def require_admin(current_user: User = Depends(get_current_user)):
    if not roles.is_admin(current_user.role):
        raise HTTPException(status_code=403, detail="Nur Admin erlaubt")
    return current_user

def get_company_id(current_user: User = Depends(get_current_user)) -> int | None:
    """Superadmin hat keine company_id → sieht alles."""
    if current_user.role == roles.SUPERADMIN:
        return None
    return current_user.fk_company

def require_write(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role == roles.READONLY:
        raise HTTPException(status_code=403, detail="Kein Schreibzugriff")
    return current_user

def require_roles(*allowed_roles: str):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return user
    return role_checker


@router.get("/me")
async def me(db: db_dependency, user: User = Depends(get_current_user)):
    company = await db.get(Company, user.fk_company) if user.fk_company else None
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "fk_company": user.fk_company,
        "company_name": company.name if company else None,
    }


@router.get("/refresh_token")
@router.get("/refresh_tokens")
async def refresh_token(
    db: db_dependency,
    refresh_token: str = Cookie(),
):
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    token_entry = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    token_entry = token_entry.scalars().first()
    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = await db.execute(select(User).where(User.id == token_entry.user_id))
    user = user.scalars().first()

    # Alten Refresh-Token immer verwerfen
    await db.delete(token_entry)
    await db.commit()

    if user is None or not user.is_active or not await _company_is_active(user, db):
        raise HTTPException(status_code=401, detail="User deaktiviert")

    new_refresh_token = await _issue_refresh_token(user, db)
    new_access_token = create_access_token(user, timedelta(minutes=1))

    response = JSONResponse(content={"message": "Token refreshed"})
    _set_auth_cookies(response, new_access_token, new_refresh_token, access_max_age=60)
    return response


@router.post("/logout")
async def logout(db: db_dependency, refresh_token: str | None = Cookie(default=None)):
    if refresh_token:
        token_entry = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
        token_entry = token_entry.scalars().first()
        if token_entry:
            await db.delete(token_entry)
            await db.commit()

    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return response


@router.get("/admin", response_model=bool)
async def has_admin_permission(user: User = Depends(get_current_user)):
    return roles.is_admin(user.role)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change_password")
async def change_password(data: ChangePasswordRequest, db: db_dependency,
                          user: User = Depends(get_current_user)):
    if not bcrypt_context.verify(data.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Altes Passwort ist falsch")
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Neues Passwort muss mindestens 8 Zeichen haben")
    user.hashed_password = bcrypt_context.hash(data.new_password)
    await db.commit()
    return {"detail": "Passwort geändert"}
