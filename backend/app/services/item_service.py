from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.item import Item

async def create_default_item(db: AsyncSession):
    # Überprüfen, ob das Standard-Item bereits existiert
    result = await db.execute(select(Item).filter(Item.name == "Standard Item"))
    existing_item = result.scalar_one_or_none()

    if not existing_item:
        db_item = Item(name="Standard Item", description="Dies ist ein Standard-Item")
        db.add(db_item)
        await db.commit()  # Speichern
        await db.refresh(db_item)  # Lade das gespeicherte Item
        return db_item
    return None
