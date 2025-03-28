from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate
from app.schemas.item import ItemResponse


router = APIRouter()

@router.get("/items", tags=["Items"])
async def get_items(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items

@router.post("/items", tags=["Items"])
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_item = Item(name=item.name, description=item.description)
        db.add(db_item)  # ✅ Erst hinzufügen
        await db.commit()
        await db.refresh(db_item)  # ✅ Danach refreshen

        return {"id": db_item.id, "name": db_item.name, "description": db_item.description}
    except Exception as e:
        print(f"Error creating item: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")