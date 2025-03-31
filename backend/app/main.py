from fastapi import FastAPI
from app.routers import items, components
from app.database.database import create_tables
app = FastAPI()
app.include_router(items.router)
app.include_router(components.router)

@app.on_event("startup")
async def startup():
    await create_tables()
@app.get('/')
def index():
    return {'message': 'hello world'}
