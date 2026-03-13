# The Core Entities
**Users Table**
  id (PK)
  username / email
  password_hash
  preferred_unit (Enum: KM or Miles)

**Bicycles Table** 
  id (PK)
  user_id (FK -> Users)
  name (e.g., "Canyon Grizl")
  total_odometer (Float) — The sum of all rides + initial mileage.
  is_active (Boolean)

**Rides (Activities) Table**
  id (PK)
  bike_id (FK -> Bicycles)
  date (DateTime)
  distance (Float)
  notes (Text)
  Logic: When a record is added here, the Bicycle.total_odometer and all associated Component.current_distance values must increment.

## The Maintenance Logic
**Components Table**
  id (PK)
  bike_id (FK -> Bicycles)
  part_type (e.g., "Chain", "Brake Pads", "Tire")
  brand_model (Text)
  distance_at_install (Float) — Odometer of the bike when this part was put on.
  current_distance (Float) — Calculated: (Bike Odometer - distance_at_install).
  lifespan_limit (Float) — User-defined threshold (e.g., 3000km).

**ServiceRecords Table**
  id (PK)
  component_id (FK -> Components)
  service_date (DateTime)
  work_performed (e.g., "Clean & Lube", "Replacement")
  cost (Decimal)

# Relationship Summary
  **One-to-Many:** One User has many Bicycles.
  **One-to-Many:** One Bicycle has many Rides.
  **One-to-Many:** One Bicycle has many Components.
  **One-to-Many:** One Component has many ServiceRecords.
