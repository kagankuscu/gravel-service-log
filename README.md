# Gravel Service Log 🚴‍♂️🔧

A specialized platform designed for cyclists to track bicycle mileage and component lifespan. This application helps maintain your gear by monitoring wear based on actual distance traveled and alerting you when components reach their service limits.

## 🌟 Key Features

- **Multi-Bike Management:** Track multiple bicycles with individual odometers.
- **Component Lifecycle Tracking:** Monitor wear on specific parts (chains, tires, brake pads) based on bike mileage.
- **Ride Logging:** Log rides to automatically update bike and component distances.
- **Service Records:** Maintain a history of maintenance activities (cleaning, lubing, replacements).
- **Wear Alerts:** Dashboard overview of components approaching their lifespan limits.
- **Unit Support:** Toggle between Kilometers and Miles.

## 🛠 Tech Stack

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **ORM:** [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (Modern async-style syntax)
- **Database:** [PostgreSQL](https://www.postgresql.org/)
- **Validation:** [Pydantic v2](https://docs.pydantic.dev/)
- **Security:** JWT Authentication via HTTPBearer

### Frontend
- **Framework:** [Svelte 5](https://svelte.dev/) (utilizing the new **Runes** system: `$state`, `$derived`)
- **Styling:** [Tailwind CSS](https://tailwindcss.com/)
- **Icons:** [Lucide React](https://lucide.dev/guide/packages/lucide-react)
- **Language:** TypeScript
- **State Management:** Svelte Runes & Native Fetch API

## 📂 Project Structure

```text
.
├── backend/app        # FastAPI application logic
├── frontend/          # Svelte 5 frontend
├── TABLES.md          # Detailed Database Schema
└── ENDPOINTS.md       # Detailed API Documentation
```

## 🏗 Database Schema

The system uses a relational model to link users, their bikes, and the components attached to those bikes:

- **Users:** Authentication and preferences (KM/Miles).
- **Bicycles:** Total odometer tracking.
- **Rides:** Trigger logic to increment distance across the bike and all active components.
- **Components:** Tracks distance relative to install date vs. lifespan limits.
- **Service Records:** Detailed maintenance history for individual components.

For a full field breakdown, see [TABLES.md](./TABLES.md).

## 🚀 API Endpoints

The backend exposes a RESTful API organized into the following modules:

- `/auth`: Registration and JWT login.
- `/bikes`: CRUD operations for bicycle management.
- `/rides`: Ride logging (core logic for distance updates).
- `/components`: Component tracking and wear status.
- `/service`: Maintenance history logging.

For the full specification, see [ENDPOINTS.md](./ENDPOINTS.md).

## 🛠 Development Setup

### Backend
1. Navigate to `/backend`.
2. Install dependencies (e.g., `pip install -r requirements.txt`).
3. Configure your `.env` with PostgreSQL credentials.
4. Run the server: `uvicorn app.main:app --reload`.

### Frontend
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Start the development server: `npm run dev`.

---
*Built for the gravel community to keep every ride smooth and every component in peak condition.*
