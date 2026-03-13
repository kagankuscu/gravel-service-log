# Project: Gravel Service Log

- Project for tracking the **bike** and **components** kilometre information.

## Tech Stack

### Backend Stack

- Python (FastAPI)
- Sqlalchemy 2.0 (modern way use syntax)
- Postgress DB
- Pydantic and Pydantic-Settings 

### Frontend Stack

- **Runes:** Svelte 5 (with its new Runes system)
- **State management:** $state and $derived
- **Api client:** fetch
- **Icons:** Lucide React
- **Language:** TypeScript
- **Styling:** Tailwind CSS

## Tables

This is file database tables
@./TABLES.md

## Endpoints

This is file endpoint for python FastAPI
@./ENDPOINTS.md

## DTO Layer

Create for all method different dto layer models
For Examples:

1. XXXCreate (UserCreate)
2. XXXUpdate (UserUpdate)
3. XXXDelete (UserDelete)
4. XXXRead   (UserRead)

## Feature	Tool / Approach

Validation	Use Pydantic models (e.g., RideCreate, RideRead).
Dependency Injection	Inject the get_db session into every route.
Background Tasks	For heavy calculations or syncs, use FastAPI's BackgroundTasks.
Security	Use HTTPBearer to protect all routes except /auth.

## Coding Standards

- **File Orginazation:** 
  - `/backend/app`: This folder for backend application (Python FastAPI)
  - `/frontend/`: This is folder for fronend application (Svelte 5)

