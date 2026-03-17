from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import auth, bikes, components, rides, service


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Gravel Service Log API",
    description="API for tracking bicycle mileage and component lifespan",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(bikes.router)
app.include_router(rides.router)
app.include_router(components.router)
app.include_router(service.router)


@app.get("/")
async def root():
    return {"message": "Gravel Service Log API"}
