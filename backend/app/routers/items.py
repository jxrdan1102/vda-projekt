from http.client import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

@router.get('')
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items

@router.get('/{id}')
async def get_item(id: int, db: AsyncSession = Depends(get_db)):
    db_item = await db.execute(select(Item).where(Item.id == id))
    db_item.scalar_one_or_none()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return db_item


@router.post('/')
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@router.put('/{id}')
async def update_item(id: int, item: ItemUpdate, db: AsyncSession = Depends(get_db)):
    # Item aus der Datenbank holen
    result = await db.execute(select(Item).where(Item.id == id))
    db_item = result.scalar_one_or_none()

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Nur die übergebenen Felder aktualisieren
    update_data = item.model_dump(exclude_unset=True)  # Nur vorhandene Werte nehmen
    for key, value in update_data.items():
        setattr(db_item, key, value)  # Dynamische Feldaktualisierung

    await db.commit()
    await db.refresh(db_item)

    return db_item

@router.delete('/{id}')
async def delete_item(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item).where(Item.id == id))
    db_item = result.scalar_one_or_none()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    await db.delete(db_item)
    await db.commit()
    return {"message": f"Item with id {id} has been deleted"}