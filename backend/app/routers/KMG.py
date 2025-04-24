from app.database.database import get_db
from app.database.generic_methods import get_all_generic, get_by_id, update_model
from app.models import KMG
from app.schemas.kmg import KMGCreate, KMGUpdate, KMGResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/kmgs", tags=["KMGs"])


@router.get("/", response_model=list[KMGResponse])
async def get_all_kmgs(db: AsyncSession = Depends(get_db)):
    return await get_all_generic(KMG, db, KMGResponse)


@router.get("/{kmg_id}", response_model=KMGResponse)
async def get_kmg(kmg_id: int, db: AsyncSession = Depends(get_db)):
    return await get_by_id(KMG, kmg_id, db, KMGResponse)


@router.post("/", response_model=KMGResponse)
async def create_kmg(kmg: KMGCreate, db: AsyncSession = Depends(get_db)):
    new_kmg = KMG(**kmg.dict())
    db.add(new_kmg)
    await db.commit()
    await db.refresh(new_kmg)
    return new_kmg


@router.put("/{kmg_id}", response_model=KMGResponse)
async def update_kmg(kmg_id: int, kmg_data: KMGUpdate, db: AsyncSession = Depends(get_db)):
    return await update_model(
        db=db,
        model_class=KMG,
        id=kmg_id,
        update_data=kmg_data.dict(exclude_unset=True)
    )

@router.delete("/{kmg_id}")
async def delete_kmg(kmg_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(KMG, kmg_id)
    if not obj:
        raise HTTPException(status_code=404, detail="KMG not found")
    await db.delete(obj)
    await db.commit()
    return {"deleted": kmg_id}