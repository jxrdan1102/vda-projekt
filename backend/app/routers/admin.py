from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from pydantic import BaseModel

from app.database.database import get_db
from app.models.user import User
from app.models.company import Company
from app.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"
    fk_company: int | None = None


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    fk_company: int | None = None

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    name: str


class RoleUpdate(BaseModel):
    role: str


def require_superadmin(current_user: User = Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Nur Superadmin erlaubt")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["superadmin", "admin"]:
        raise HTTPException(status_code=403, detail="Nur Admin erlaubt")
    return current_user


@router.get("/companies")
async def list_companies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    result = await db.execute(select(Company))
    companies = result.scalars().all()
    return [{"id": c.id, "name": c.name} for c in companies]


@router.post("/companies")
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    company = Company(name=data.name)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return {"id": company.id, "name": company.name}


@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    await db.delete(company)
    await db.commit()
    return {"detail": f"Firma {company_id} gelöscht"}


@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if current_user.role == "superadmin":
        result = await db.execute(select(User))
    else:
        result = await db.execute(
            select(User).where(User.fk_company == current_user.fk_company)
        )
    return [UserOut.model_validate(u) for u in result.scalars().all()]


@router.post("/companies/{company_id}/admin")
async def create_admin_for_company(
    company_id: int,
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_superadmin)
):
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    user = User(
        username=data.username,
        hashed_password=pwd_context.hash(data.password),
        role="admin",
        fk_company=company_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.post("/users")
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if current_user.role == "admin":
        if data.role not in ["user", "readonly"]:
            raise HTTPException(status_code=403, detail="Admin kann nur user/readonly anlegen")
        fk_company = current_user.fk_company
    else:
        fk_company = data.fk_company

    user = User(
        username=data.username,
        hashed_password=pwd_context.hash(data.password),
        role=data.role,
        fk_company=fk_company,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.patch("/users/{user_id}/role")
async def change_role(
    user_id: int,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if data.role not in ["user", "readonly", "admin", "superadmin"]:
        raise HTTPException(status_code=400, detail="Ungültige Rolle")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")

    if current_user.role == "admin":
        if user.fk_company != current_user.fk_company:
            raise HTTPException(status_code=403, detail="Kein Zugriff")
        if data.role not in ["user", "readonly"]:
            raise HTTPException(status_code=403, detail="Admin kann nur user/readonly setzen")

    if user.role == "superadmin" and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin kann nicht geändert werden")

    user.role = data.role
    await db.commit()
    return {"detail": f"Rolle auf {data.role} gesetzt"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")

    if user.role == "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin kann nicht gelöscht werden")

    if current_user.role == "admin" and user.fk_company != current_user.fk_company:
        raise HTTPException(status_code=403, detail="Kein Zugriff")

    await db.delete(user)
    await db.commit()
    return {"detail": f"User {user.username} gelöscht"}


@router.patch("/users/{user_id}/password")
async def change_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")

    if current_user.role == "admin" and user.fk_company != current_user.fk_company:
        raise HTTPException(status_code=403, detail="Kein Zugriff")

    user.hashed_password = pwd_context.hash(new_password)
    await db.commit()
    return {"detail": "Passwort geändert"}


@router.get("/is-admin")
async def is_admin(current_user: User = Depends(get_current_user)):
    return current_user.role in ["admin", "superadmin"]