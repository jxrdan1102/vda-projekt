from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models import ANAMU
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.anakomp import AnakompUpdateR
from app.schemas.anakonst import AnakonstUpdateR
from app.schemas.anamu import AnamuCreateR
from app.schemas.anamu import AnamuGetIdR
from app.schemas.anamu import AnamuGetR
from app.services import AnamuService
from app.services.AnamuService import calc_uncertainty

router = APIRouter(prefix="/anamu", tags=["anamu"])


@router.get("/r", response_model=list[AnamuGetR])
async def get_all_anamusr(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    stmt = select(ANAMU).where(ANAMU.fk_user == current_user.id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{id}/r", response_model=AnamuGetIdR)
async def get_anamu_by_idr(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await AnamuService.get_anamu_by_id(db, id, current_user.id)


@router.post("/r")
async def create_anamur(anamu: AnamuCreateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await AnamuService.create_anamu_with_dependencies(db, anamu, current_user.id)
    return {"detail": "Analyseprojekt wurde erfolgreich erstellt"}


@router.put("/anakomp/{id}/r")
async def update_anakompr(id: int, anakomp: AnakompUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await AnamuService.update_anakompr(db, id, anakomp.model_dump(exclude_unset=True), current_user.id)
    return {"detail": "Komponente wurde erfolgreich geändert"}


@router.put("/anakonst/{id}/r")
async def update_anakonstr(id: int, anakonst: AnakonstUpdateR, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await AnamuService.update_anakonstr(db, id, anakonst.model_dump(exclude_unset=True), current_user.id)
    return {"detail": "Konstante wurde erfolgreich geändert"}

@router.get("/{id}/calc/r")
async def calc_uncertainty_route(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):

    return await calc_uncertainty(db, id, current_user.id)

@router.delete("/{id}")
async def delete_anamu_by_id(id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    await AnamuService.delete_anamu(db, id, current_user.id)
    return {"detail": f"Analyseprojekt mit ID {id} wurde gelöscht"}

