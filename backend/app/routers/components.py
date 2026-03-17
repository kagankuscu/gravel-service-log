from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import get_current_user
from app.models import Bicycle, Component, User
from app.schemas import ComponentCreate, ComponentOut, ComponentPatch, ComponentStatusOut

router = APIRouter(prefix="/components", tags=["components"])


@router.get("", response_model=list[ComponentOut])
async def list_components(
    bike_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _assert_bike_owned(bike_id, current_user.id, db)
    result = await db.execute(select(Component).where(Component.bike_id == bike_id))
    return result.scalars().all()


@router.get("/status", response_model=list[ComponentStatusOut])
async def components_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Dashboard: all active components across the user's bikes, with wear percentage."""
    result = await db.execute(
        select(Component)
        .join(Bicycle, Component.bike_id == Bicycle.id)
        .where(
            Bicycle.user_id == current_user.id,
            Component.is_active == True,
            Component.lifespan_limit.isnot(None),
        )
    )
    components = result.scalars().all()
    out = []
    for c in components:
        wear = (c.current_distance / c.lifespan_limit * 100) if c.lifespan_limit else None
        out.append(ComponentStatusOut.model_validate(c, update={"wear_percentage": wear}))
    return out


@router.post("", response_model=ComponentOut, status_code=status.HTTP_201_CREATED)
async def create_component(
    body: ComponentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _assert_bike_owned(body.bike_id, current_user.id, db)
    component = Component(**body.model_dump())
    db.add(component)
    await db.commit()
    await db.refresh(component)
    return component


@router.patch("/{component_id}", response_model=ComponentOut)
async def patch_component(
    component_id: int,
    body: ComponentPatch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    component = await _get_owned_component(component_id, current_user.id, db)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(component, field, value)
    await db.commit()
    await db.refresh(component)
    return component


async def _assert_bike_owned(bike_id: int, user_id: int, db: AsyncSession) -> None:
    result = await db.execute(
        select(Bicycle).where(Bicycle.id == bike_id, Bicycle.user_id == user_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Bike not found")


async def _get_owned_component(component_id: int, user_id: int, db: AsyncSession) -> Component:
    result = await db.execute(
        select(Component)
        .join(Bicycle, Component.bike_id == Bicycle.id)
        .where(Component.id == component_id, Bicycle.user_id == user_id)
    )
    component = result.scalar_one_or_none()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return component
