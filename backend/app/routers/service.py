from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Bicycle, Component, ServiceRecord, User
from app.schemas import ServiceCreate, ServiceOut

router = APIRouter(prefix="/service", tags=["service"])


@router.get("/{component_id}", response_model=list[ServiceOut])
async def list_service_records(
    component_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _assert_component_owned(component_id, current_user.id, db)
    result = await db.execute(
        select(ServiceRecord)
        .where(ServiceRecord.component_id == component_id)
        .order_by(ServiceRecord.service_date.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ServiceOut, status_code=status.HTTP_201_CREATED)
async def create_service_record(
    body: ServiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _assert_component_owned(body.component_id, current_user.id, db)
    record = ServiceRecord(
        component_id=body.component_id,
        work_performed=body.work_performed,
        service_date=body.service_date or datetime.utcnow(),
        cost=body.cost,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_record(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ServiceRecord)
        .join(Component, ServiceRecord.component_id == Component.id)
        .join(Bicycle, Component.bike_id == Bicycle.id)
        .where(ServiceRecord.id == service_id, Bicycle.user_id == current_user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Service record not found")
    await db.delete(record)
    await db.commit()


async def _assert_component_owned(component_id: int, user_id: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(Component)
        .join(Bicycle, Component.bike_id == Bicycle.id)
        .where(Component.id == component_id, Bicycle.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Component not found")
