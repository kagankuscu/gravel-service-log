from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr
from app.models import UnitEnum


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    preferred_unit: UnitEnum = UnitEnum.KM


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    preferred_unit: UnitEnum

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Bikes ─────────────────────────────────────────────────────────────────────

class BikeCreate(BaseModel):
    name: str
    brand: str | None = None
    initial_odometer: float = 0.0


class BikeUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    is_active: bool | None = None


class BikeOut(BaseModel):
    id: int
    name: str
    brand: str | None
    total_odometer: float
    is_active: bool

    model_config = {"from_attributes": True}


# ── Rides ─────────────────────────────────────────────────────────────────────

class RideCreate(BaseModel):
    bike_id: int
    distance: float
    date: datetime | None = None
    notes: str | None = None


class RideOut(BaseModel):
    id: int
    bike_id: int
    date: datetime
    distance: float
    notes: str | None

    model_config = {"from_attributes": True}


# ── Components ────────────────────────────────────────────────────────────────

class ComponentCreate(BaseModel):
    bike_id: int
    part_type: str
    brand_model: str | None = None
    distance_at_install: float = 0.0
    lifespan_limit: float | None = None


class ComponentPatch(BaseModel):
    brand_model: str | None = None
    lifespan_limit: float | None = None
    is_active: bool | None = None


class ComponentOut(BaseModel):
    id: int
    bike_id: int
    part_type: str
    brand_model: str | None
    distance_at_install: float
    current_distance: float
    lifespan_limit: float | None
    is_active: bool

    model_config = {"from_attributes": True}


class ComponentStatusOut(ComponentOut):
    wear_percentage: float | None = None


# ── Service Records ───────────────────────────────────────────────────────────

class ServiceCreate(BaseModel):
    component_id: int
    work_performed: str
    service_date: datetime | None = None
    cost: Decimal | None = None


class ServiceOut(BaseModel):
    id: int
    component_id: int
    service_date: datetime
    work_performed: str
    cost: Decimal | None

    model_config = {"from_attributes": True}
