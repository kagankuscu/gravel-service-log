1. **Authentication**
    **POST** /auth/register - Create a new user account.
    **POST** /auth/login - Exchange credentials for a JWT access token.
    **GET** /auth/me - Get current user profile and unit preferences (KM vs Miles).

2. **Bicycles**
    **GET** /bikes - List all bikes for the authenticated user.
    **POST** /bikes - Register a new bicycle (Name, Brand, Initial Odometer).
    **GET** /bikes/{id} - Get detailed stats for a specific bike.
    **PUT** /bikes/{id} - Update bike details (e.g., nickname or status).
    **DELETE** /bikes/{id} - Remove a bike from the garage.

3. **Ride Logs**
    **GET** /rides - List all ride history (support query params: ?bike_id=123).
    **POST** /rides - The Core Trigger: Post distance, date, and bike ID.
        Logic: This endpoint triggers the background update for the bike's odometer and all active component wear.
    **GET** /rides/{id} - View specific ride details.
    **DELETE** /rides/{id} - Delete a ride (requires a "revert" logic for odometer/component wear).

4. **Components & Maintenance**
    **GET** /components?bike_id={id} - Get all parts currently attached to a specific bike.
    **POST** /components - Add a new part to a bike (e.g., "New Chain" at 500km).
    **PATCH** /components/{id} - Update a component (e.g., mark as "Retired" or "Active").
    **GET** /components/status - Dashboard Endpoint: Returns all components approaching their lifespan_limit.

5. **Service Records**
    **GET** /service/{component_id} - History of maintenance for a specific part.
    **POST** /service - Log a service event (e.g., "Bled brakes" or "Luricated chain").
    **DELETE** /service/{id} - Remove a service log entry.
