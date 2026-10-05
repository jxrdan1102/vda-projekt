from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import roles
from app.database.database import get_db
from app.models.ANAMU import ANAKOMP, ANAKONST, ANAMU
from app.models.company import Company
from app.models.components import Component
from app.models.kmg import KMG
from app.models.modell import Modell
from app.models.RefreshToken import RefreshToken
from app.models.user import User
from app.routers.auth import bcrypt_context, get_current_user, require_admin, require_superadmin

router = APIRouter(prefix="/admin", tags=["admin"])

MIN_PASSWORD_LENGTH = 8

# Tabellen mit Nutzdaten, die an User (fk_user_id) und Firma (fk_company) hängen
DATA_MODELS = (Modell, Component, ANAMU, ANAKOMP, ANAKONST, KMG)


# ── Schemas ──

class CompanyCreate(BaseModel):
    name: str
    # optional direkt den ersten Firmen-Admin mit anlegen
    admin_username: str | None = None
    admin_password: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None


class CompanyOut(BaseModel):
    id: int
    name: str
    is_active: bool
    user_count: int = 0


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = roles.USER
    fk_company: int | None = None  # nur Superadmin; Admin legt immer in eigener Firma an


class UserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None
    fk_company: int | None = None  # nur Superadmin


class PasswordReset(BaseModel):
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    fk_company: int | None = None
    company_name: str | None = None
    is_active: bool = True


# ── Hilfsfunktionen ──

def _user_out(user: User, company_names: dict[int, str]) -> UserOut:
    out = UserOut.model_validate(user)
    out.company_name = company_names.get(user.fk_company) if user.fk_company else None
    return out


async def _company_names(db: AsyncSession) -> dict[int, str]:
    result = await db.execute(select(Company.id, Company.name))
    return {cid: name for cid, name in result.all()}


def _check_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(status_code=400, detail=f"Passwort muss mindestens {MIN_PASSWORD_LENGTH} Zeichen haben")


async def _check_username_free(db: AsyncSession, username: str) -> None:
    if not username.strip():
        raise HTTPException(status_code=400, detail="Benutzername darf nicht leer sein")
    result = await db.execute(select(User.id).where(User.username == username))
    if result.first() is not None:
        raise HTTPException(status_code=409, detail="Benutzername ist bereits vergeben")


async def _has_data(db: AsyncSession, column: str, value: int) -> bool:
    for model in DATA_MODELS:
        stmt = select(func.count()).select_from(model).where(getattr(model, column) == value)
        if (await db.execute(stmt)).scalar_one():
            return True
    return False


async def _get_company_or_404(db: AsyncSession, company_id: int) -> Company:
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    return company


async def _get_user_or_404(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")
    return user


def _check_can_manage(actor: User, target: User) -> None:
    """Darf actor den Nutzer target bearbeiten / löschen?"""
    if actor.role == roles.SUPERADMIN:
        return
    # Firmen-Admin: nur normale Nutzer der eigenen Firma, nicht sich selbst
    if target.fk_company != actor.fk_company:
        raise HTTPException(status_code=403, detail="Kein Zugriff auf Nutzer anderer Firmen")
    if target.id == actor.id:
        raise HTTPException(status_code=403, detail="Eigenes Konto kann hier nicht geändert werden")
    if target.role not in roles.ADMIN_ASSIGNABLE_ROLES:
        raise HTTPException(status_code=403, detail="Admins können nur vom Superadmin geändert werden")


async def _ensure_not_last_superadmin(db: AsyncSession, target: User) -> None:
    if target.role != roles.SUPERADMIN:
        return
    result = await db.execute(
        select(func.count(User.id)).where(User.role == roles.SUPERADMIN, User.is_active.is_(True))
    )
    if result.scalar_one() <= 1:
        raise HTTPException(status_code=400, detail="Der letzte aktive Superadmin kann nicht entfernt werden")


async def _resolve_company_for_new_user(db: AsyncSession, actor: User, role: str, fk_company: int | None) -> int | None:
    if role not in roles.assignable_roles(actor.role):
        raise HTTPException(status_code=403, detail=f"Rolle '{role}' darf nicht vergeben werden")

    if actor.role == roles.ADMIN:
        if fk_company is not None and fk_company != actor.fk_company:
            raise HTTPException(status_code=403, detail="Nur User in eigener Firma erlaubt")
        return actor.fk_company

    # Superadmin
    if role == roles.SUPERADMIN:
        return None
    if fk_company is None:
        raise HTTPException(status_code=400, detail="Bitte eine Firma angeben")
    await _get_company_or_404(db, fk_company)
    return fk_company


# ── Firmen (nur Superadmin) ──

@router.get("/companies", response_model=list[CompanyOut], dependencies=[Depends(require_superadmin)])
async def list_companies(db: AsyncSession = Depends(get_db)):
    counts = dict(
        (await db.execute(select(User.fk_company, func.count(User.id)).group_by(User.fk_company))).all()
    )
    result = await db.execute(select(Company).order_by(Company.name))
    return [
        CompanyOut(id=c.id, name=c.name, is_active=bool(c.is_active), user_count=counts.get(c.id, 0))
        for c in result.scalars().all()
    ]


@router.post("/companies", response_model=CompanyOut, dependencies=[Depends(require_superadmin)])
async def create_company(data: CompanyCreate, db: AsyncSession = Depends(get_db)):
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Firmenname darf nicht leer sein")

    with_admin = bool(data.admin_username)
    if with_admin:
        _check_password(data.admin_password or "")
        await _check_username_free(db, data.admin_username)

    company = Company(name=data.name.strip(), is_active=True)
    db.add(company)
    await db.flush()

    if with_admin:
        db.add(User(
            username=data.admin_username,
            hashed_password=bcrypt_context.hash(data.admin_password),
            role=roles.ADMIN,
            fk_company=company.id,
            is_active=True,
        ))

    await db.commit()
    await db.refresh(company)
    return CompanyOut(id=company.id, name=company.name, is_active=True, user_count=1 if with_admin else 0)


@router.patch("/companies/{company_id}", response_model=CompanyOut, dependencies=[Depends(require_superadmin)])
async def update_company(company_id: int, data: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    company = await _get_company_or_404(db, company_id)
    if data.name is not None:
        if not data.name.strip():
            raise HTTPException(status_code=400, detail="Firmenname darf nicht leer sein")
        company.name = data.name.strip()
    if data.is_active is not None:
        company.is_active = data.is_active
    await db.commit()
    await db.refresh(company)
    count = (await db.execute(select(func.count(User.id)).where(User.fk_company == company.id))).scalar_one()
    return CompanyOut(id=company.id, name=company.name, is_active=bool(company.is_active), user_count=count)


@router.delete("/companies/{company_id}", dependencies=[Depends(require_superadmin)])
async def delete_company(company_id: int, db: AsyncSession = Depends(get_db)):
    company = await _get_company_or_404(db, company_id)
    count = (await db.execute(select(func.count(User.id)).where(User.fk_company == company.id))).scalar_one()
    if count:
        raise HTTPException(status_code=409, detail="Firma hat noch Nutzer – bitte erst Nutzer entfernen oder Firma deaktivieren")
    if await _has_data(db, "fk_company", company.id):
        raise HTTPException(status_code=409, detail="Firma hat noch Daten – bitte stattdessen deaktivieren")
    try:
        await db.delete(company)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Firma hat noch Daten – bitte stattdessen deaktivieren")
    return {"detail": f"Firma {company.name} gelöscht"}


@router.post("/companies/{company_id}/admin", response_model=UserOut, dependencies=[Depends(require_superadmin)])
async def create_company_admin(company_id: int, data: UserCreate, db: AsyncSession = Depends(get_db)):
    company = await _get_company_or_404(db, company_id)
    _check_password(data.password)
    await _check_username_free(db, data.username)

    user = User(
        username=data.username,
        hashed_password=bcrypt_context.hash(data.password),
        role=roles.ADMIN,
        fk_company=company.id,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _user_out(user, {company.id: company.name})


# ── Nutzer (Superadmin: alle, Admin: eigene Firma) ──

@router.get("/users", response_model=list[UserOut])
async def list_users(
    company_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    stmt = select(User).order_by(User.username)
    if current_user.role == roles.SUPERADMIN:
        if company_id is not None:
            stmt = stmt.where(User.fk_company == company_id)
    else:
        stmt = stmt.where(User.fk_company == current_user.fk_company)
    users = (await db.execute(stmt)).scalars().all()
    names = await _company_names(db)
    return [_user_out(u, names) for u in users]


@router.post("/users", response_model=UserOut)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    fk_company = await _resolve_company_for_new_user(db, current_user, data.role, data.fk_company)
    _check_password(data.password)
    await _check_username_free(db, data.username)

    user = User(
        username=data.username,
        hashed_password=bcrypt_context.hash(data.password),
        role=data.role,
        fk_company=fk_company,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return _user_out(user, await _company_names(db))


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = await _get_user_or_404(db, user_id)
    _check_can_manage(current_user, user)

    new_role = data.role if data.role is not None else user.role
    new_company = user.fk_company

    if data.role is not None and data.role != user.role:
        if data.role not in roles.assignable_roles(current_user.role):
            raise HTTPException(status_code=403, detail=f"Rolle '{data.role}' darf nicht vergeben werden")
        await _ensure_not_last_superadmin(db, user)

    if data.fk_company is not None and data.fk_company != user.fk_company:
        if current_user.role != roles.SUPERADMIN:
            raise HTTPException(status_code=403, detail="Nur Superadmin kann die Firma ändern")
        await _get_company_or_404(db, data.fk_company)
        new_company = data.fk_company

    if new_role == roles.SUPERADMIN:
        new_company = None
    elif new_company is None:
        raise HTTPException(status_code=400, detail="Nutzer dieser Rolle brauchen eine Firma")

    if data.is_active is False:
        if user.id == current_user.id:
            raise HTTPException(status_code=400, detail="Eigenes Konto kann nicht deaktiviert werden")
        await _ensure_not_last_superadmin(db, user)

    user.role = new_role
    user.fk_company = new_company
    if data.is_active is not None:
        user.is_active = data.is_active
        if not data.is_active:
            # laufende Sessions beenden
            for token in (await db.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))).scalars():
                await db.delete(token)

    await db.commit()
    await db.refresh(user)
    return _user_out(user, await _company_names(db))


@router.post("/users/{user_id}/password")
async def reset_password(
    user_id: int,
    data: PasswordReset,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = await _get_user_or_404(db, user_id)
    if user.id != current_user.id:
        _check_can_manage(current_user, user)
    _check_password(data.password)
    user.hashed_password = bcrypt_context.hash(data.password)
    await db.commit()
    return {"detail": f"Passwort für {user.username} gesetzt"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user = await _get_user_or_404(db, user_id)
    _check_can_manage(current_user, user)
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Eigenes Konto kann nicht gelöscht werden")
    await _ensure_not_last_superadmin(db, user)
    if await _has_data(db, "fk_user_id", user.id):
        raise HTTPException(status_code=409, detail="Nutzer hat noch Daten (Modelle, Projekte …) – bitte stattdessen deaktivieren")

    username = user.username
    try:
        for token in (await db.execute(select(RefreshToken).where(RefreshToken.user_id == user.id))).scalars():
            await db.delete(token)
        await db.delete(user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Nutzer hat noch Daten (Modelle, Projekte …) – bitte stattdessen deaktivieren")
    return {"detail": f"User {username} gelöscht"}


# ── Kompatibilität mit der bisherigen API ──

class RoleUpdate(BaseModel):
    role: str


@router.patch("/users/{user_id}/role", response_model=UserOut)
async def change_role(
    user_id: int,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await update_user(user_id, UserUpdate(role=data.role), db, current_user)


@router.patch("/users/{user_id}/password")
async def change_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await reset_password(user_id, PasswordReset(password=new_password), db, current_user)


@router.get("/is-admin", response_model=bool)
async def is_admin(current_user: User = Depends(get_current_user)):
    return roles.is_admin(current_user.role)
