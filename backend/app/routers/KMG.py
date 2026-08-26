from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db
from app.models import KMG
from app.models.user import User
from app.routers.auth import get_current_user, get_company_id, require_write
from app.schemas.kmg import KMGCreate, KMGResponse, KMGUpdate

router = APIRouter(prefix="/kmgs", tags=["KMGs"])


@router.get("", response_model=list[KMGResponse])
async def get_all_kmgs(
    db: AsyncSession = Depends(get_db),
    company_id: int | None = Depends(get_company_id)
):
    stmt = select(KMG)
    if company_id is not None:
        stmt = stmt.where(KMG.fk_company == company_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{kmg_id}", response_model=KMGResponse)
async def get_kmg(
    kmg_id: int,
    db: AsyncSession = Depends(get_db),
    company_id: int | None = Depends(get_company_id)
):
    stmt = select(KMG).where(KMG.id == kmg_id)
    if company_id is not None:
        stmt = stmt.where(KMG.fk_company == company_id)
    result = await db.execute(stmt)
    kmg = result.scalar_one_or_none()
    if not kmg:
        raise HTTPException(status_code=404, detail="KMG nicht gefunden")
    return kmg


@router.post("", response_model=KMGResponse)
async def create_kmg(
    kmg: KMGCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    new_kmg = KMG(**kmg.model_dump(), fk_user_id=current_user.id, fk_company=company_id)
    db.add(new_kmg)
    await db.commit()
    await db.refresh(new_kmg)
    return new_kmg


@router.put("/{kmg_id}", response_model=KMGResponse)
async def update_kmg(
    kmg_id: int,
    kmg_data: KMGUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    stmt = select(KMG).where(KMG.id == kmg_id)
    if company_id is not None:
        stmt = stmt.where(KMG.fk_company == company_id)
    result = await db.execute(stmt)
    kmg = result.scalar_one_or_none()
    if not kmg:
        raise HTTPException(status_code=404, detail="KMG nicht gefunden")
    for key, value in kmg_data.model_dump(exclude_unset=True).items():
        setattr(kmg, key, value)
    await db.commit()
    await db.refresh(kmg)
    return kmg


@router.delete("/{kmg_id}")
async def delete_kmg(
    kmg_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_write),
    company_id: int | None = Depends(get_company_id)
):
    stmt = select(KMG).where(KMG.id == kmg_id)
    if company_id is not None:
        stmt = stmt.where(KMG.fk_company == company_id)
    result = await db.execute(stmt)
    kmg = result.scalar_one_or_none()
    if not kmg:
        raise HTTPException(status_code=404, detail="KMG nicht gefunden")
    await db.delete(kmg)
    await db.commit()
    return {"deleted": kmg_id}