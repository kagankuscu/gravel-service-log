from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Bicycle, User
from app.schemas import BikeCreate, BikeOut, BikeUpdate

router = APIRouter(prefix="/bikes", tags=["bikes"])


@router.get("", response_model=list[BikeOut])
async def list_bikes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Bicycle).where(Bicycle.user_id == current_user.id))
    return result.scalars().all()


@router.post("", response_model=BikeOut, status_code=status.HTTP_201_CREATED)
async def create_bike(
    body: BikeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bike = Bicycle(
        user_id=current_user.id,
        name=body.name,
        brand=body.brand,
        total_odometer=body.initial_odometer,
    )
    db.add(bike)
    await db.commit()
    await db.refresh(bike)
    return bike


@router.get("/{bike_id}", response_model=BikeOut)
async def get_bike(
    bike_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bike = await _get_owned_bike(bike_id, current_user.id, db)
    return bike


@router.put("/{bike_id}", response_model=BikeOut)
async def update_bike(
    bike_id: int,
    body: BikeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bike = await _get_owned_bike(bike_id, current_user.id, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(bike, field, value)
    await db.commit()
    await db.refresh(bike)
    return bike


@router.delete("/{bike_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bike(
    bike_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bike = await _get_owned_bike(bike_id, current_user.id, db)
    await db.delete(bike)
    await db.commit()


async def _get_owned_bike(bike_id: int, user_id: int, db: AsyncSession) -> Bicycle:
    result = await db.execute(
        select(Bicycle).where(Bicycle.id == bike_id, Bicycle.user_id == user_id)
    )
    bike = result.scalar_one_or_none()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")
    return bike
