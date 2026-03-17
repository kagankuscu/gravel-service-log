from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Bicycle, Component, Ride, User
from app.schemas import RideCreate, RideOut

router = APIRouter(prefix="/rides", tags=["rides"])


@router.get("", response_model=list[RideOut])
async def list_rides(
    bike_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Join through Bicycle to enforce ownership
    query = (
        select(Ride)
        .join(Bicycle, Ride.bike_id == Bicycle.id)
        .where(Bicycle.user_id == current_user.id)
    )
    if bike_id is not None:
        query = query.where(Ride.bike_id == bike_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=RideOut, status_code=status.HTTP_201_CREATED)
async def create_ride(
    body: RideCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify bike ownership
    bike_result = await db.execute(
        select(Bicycle).where(Bicycle.id == body.bike_id, Bicycle.user_id == current_user.id)
    )
    bike = bike_result.scalar_one_or_none()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")

    ride = Ride(
        bike_id=body.bike_id,
        distance=body.distance,
        date=body.date or datetime.utcnow(),
        notes=body.notes,
    )
    db.add(ride)

    # Core trigger: update bike odometer and all active component distances
    bike.total_odometer += body.distance
    components_result = await db.execute(
        select(Component).where(Component.bike_id == body.bike_id, Component.is_active == True)
    )
    for component in components_result.scalars().all():
        component.current_distance += body.distance

    await db.commit()
    await db.refresh(ride)
    return ride


@router.get("/{ride_id}", response_model=RideOut)
async def get_ride(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ride = await _get_owned_ride(ride_id, current_user.id, db)
    return ride


@router.delete("/{ride_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ride(
    ride_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ride = await _get_owned_ride(ride_id, current_user.id, db)

    # Revert logic: subtract distance from bike odometer and active components
    bike_result = await db.execute(select(Bicycle).where(Bicycle.id == ride.bike_id))
    bike = bike_result.scalar_one()
    bike.total_odometer -= ride.distance

    components_result = await db.execute(
        select(Component).where(Component.bike_id == ride.bike_id, Component.is_active == True)
    )
    for component in components_result.scalars().all():
        component.current_distance = max(0.0, component.current_distance - ride.distance)

    await db.delete(ride)
    await db.commit()


async def _get_owned_ride(ride_id: int, user_id: int, db: AsyncSession) -> Ride:
    result = await db.execute(
        select(Ride)
        .join(Bicycle, Ride.bike_id == Bicycle.id)
        .where(Ride.id == ride_id, Bicycle.user_id == user_id)
    )
    ride = result.scalar_one_or_none()
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride
