from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.models.user import User
from app.models.company import Company
from app.routers.auth import get_current_user, require_superadmin, require_admin
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter(prefix="/admin", tags=["admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class CompanyCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"  # user, readonly
    fk_company: int | None = None

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    fk_company: int | None = None
    class Config:
        from_attributes = True

# ── Superadmin: Firma anlegen ──
@router.post("/companies", dependencies=[Depends(require_superadmin)])
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db)
):
    company = Company(name=data.name)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return {"id": company.id, "name": company.name}

# ── Superadmin: Admin für Firma anlegen ──
@router.post("/companies/{company_id}/admin", dependencies=[Depends(require_superadmin)])
async def create_admin(
    company_id: int,
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
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

# ── Admin: User innerhalb seiner Firma anlegen ──
@router.post("/users", dependencies=[Depends(require_admin)])
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admin kann nur User in seiner eigenen Firma anlegen
    if current_user.role == "admin":
        if data.fk_company and data.fk_company != current_user.fk_company:
            raise HTTPException(status_code=403, detail="Nur User in eigener Firma erlaubt")
        fk_company = current_user.fk_company
    else:
        # Superadmin kann überall
        fk_company = data.fk_company

    # Admin kann keine Admins anlegen — nur user/readonly
    if current_user.role == "admin" and data.role not in ["user", "readonly"]:
        raise HTTPException(status_code=403, detail="Admin kann nur user/readonly anlegen")

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

# ── Admin: User seiner Firma auflisten ──
@router.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "superadmin":
        result = await db.execute(select(User))
    else:
        result = await db.execute(
            select(User).where(User.fk_company == current_user.fk_company)
        )
    users = result.scalars().all()
    return [UserOut.model_validate(u) for u in users]

# ── Admin: User löschen ──
@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")
    
    # Admin kann nur User seiner Firma löschen
    if current_user.role == "admin" and user.fk_company != current_user.fk_company:
        raise HTTPException(status_code=403, detail="Kein Zugriff")
    
    # Niemand kann Superadmin löschen
    if user.role == "superadmin":
        raise HTTPException(status_code=403, detail="Superadmin kann nicht gelöscht werden")
    
    await db.delete(user)
    await db.commit()
    return {"detail": f"User {user.username} gelöscht"}

# ── Admin: Rolle ändern ──
@router.patch("/users/{user_id}/role")
async def change_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if role not in ["user", "readonly", "admin", "superadmin"]:
        raise HTTPException(status_code=400, detail="Ungültige Rolle")
    
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User nicht gefunden")
    
    # Admin kann nur user/readonly setzen
    if current_user.role == "admin" and role not in ["user", "readonly"]:
        raise HTTPException(status_code=403, detail="Admin kann nur user/readonly setzen")
    
    # Nur Superadmin kann Superadmin setzen
    if role == "superadmin" and current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Nur Superadmin kann Superadmin vergeben")
    
    user.role = role
    await db.commit()
    return {"detail": f"Rolle auf {role} gesetzt"}

# ── Alle Firmen auflisten (Superadmin) ──
@router.get("/companies", dependencies=[Depends(require_superadmin)])
async def list_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company))
    companies = result.scalars().all()
    return [{"id": c.id, "name": c.name} for c in companies]