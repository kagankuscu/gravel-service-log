import enum
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class UnitEnum(str, enum.Enum):
    KM = "KM"
    MILES = "MILES"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    preferred_unit: Mapped[UnitEnum] = mapped_column(
        Enum(UnitEnum), default=UnitEnum.KM
    )

    bikes: Mapped[list["Bicycle"]] = relationship(
        "Bicycle", back_populates="owner", cascade="all, delete-orphan"
    )


class Bicycle(Base):
    __tablename__ = "bicycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100))
    total_odometer: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    owner: Mapped["User"] = relationship("User", back_populates="bikes")
    rides: Mapped[list["Ride"]] = relationship(
        "Ride", back_populates="bike", cascade="all, delete-orphan"
    )
    components: Mapped[list["Component"]] = relationship(
        "Component", back_populates="bike", cascade="all, delete-orphan"
    )


class Ride(Base):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bike_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bicycles.id"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    distance: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    bike: Mapped["Bicycle"] = relationship("Bicycle", back_populates="rides")


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bike_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bicycles.id"), nullable=False
    )
    part_type: Mapped[str] = mapped_column(String(100), nullable=False)
    brand_model: Mapped[str | None] = mapped_column(Text)
    distance_at_install: Mapped[float] = mapped_column(Float, default=0.0)
    current_distance: Mapped[float] = mapped_column(Float, default=0.0)
    lifespan_limit: Mapped[float | None] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    bike: Mapped["Bicycle"] = relationship("Bicycle", back_populates="components")
    service_records: Mapped[list["ServiceRecord"]] = relationship(
        "ServiceRecord", back_populates="component", cascade="all, delete-orphan"
    )


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    component_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("components.id"), nullable=False
    )
    service_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    work_performed: Mapped[str] = mapped_column(Text, nullable=False)
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    component: Mapped["Component"] = relationship(
        "Component", back_populates="service_records"
    )
