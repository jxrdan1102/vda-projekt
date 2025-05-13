from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.modell import ModellCreateR
from app.schemas.modell import ModellGetAllR
from app.schemas.modell import ModellGetIdR
from app.schemas.modell import ModellUpdateR
from app.services import ModellService

router = APIRouter(prefix="/modells", tags=["modells"])

@router.get("/r", response_model=list[ModellGetAllR])
async def get_modellsr(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await ModellService.get_all_modells(db, current_user.id)

@router.get("/{id}/r", response_model=ModellGetIdR)
async def get_modell_by_idr(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await ModellService.get_modell_by_id(db, id, current_user.id)

@router.post("/r")
async def create_modellr(modell: ModellCreateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await ModellService.create_modell(db, modell.model_dump(), current_user.id)
    return {"detail": "Modell wurde erfolgreich erstellt"}

@router.put("/{id}/r")
async def update_modellr(id: int, modell: ModellUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await ModellService.update_modell(db, id, modell.model_dump(exclude_unset=True), current_user.id)
    return {"detail": "Modell wurde erfolgreich geändert"}

@router.delete("/{id}")
async def delete_modell_by_id(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await ModellService.delete_modell_with_components(db, id, current_user.id)
    return {"detail": f"Modell mit ID {id} wurde gelöscht"}