from app.core.security import (
    admin_required,
    create_access_token,
    get_current_user,
    get_user_by_username,
    hash_password,
    verify_password,
)
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user_service import username_exists  # 👈 hier neu
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    if await username_exists(db, user_data.username):  # 👈 neue Funktion verwenden
        raise HTTPException(status_code=400, detail="Username bereits vergeben")

    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
    )
    db.add(new_user)
    await db.commit()
    return {
        "message": "User erstellt",
        "username": new_user.username,
        "role": new_user.role,
    }


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Falsche Anmeldedaten")

    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def get_profile(user: User = Depends(get_current_user)):
    return {"username": user.username, "role": user.role}


@router.get("/admin-data")
async def get_admin_data(user: User = Depends(admin_required)):
    return {"msg": f"Hallo Admin {user.username} 🎩"}
