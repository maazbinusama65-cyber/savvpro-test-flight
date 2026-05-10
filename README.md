# ✈️ FlightHub — Flight Search & Booking System

A full-stack flight search and booking application for travel agency staff.  
**Backend:** Python (FastAPI) · **Frontend:** Node.js (Express) · **Database:** SQLite

---

## Quick Start

### 1. Clone / extract the project

```bash
git clone <your-repo-url> flighthub
cd flighthub
```

### 2. Backend

```bash
cd backend

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with 10 sample flights
python seed.py

# Start the API server
uvicorn main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

### 3. Frontend (separate terminal)

```bash
cd frontend
npm install
node server.js
```

The UI will be available at **http://localhost:3000**

---

## Running Tests

From the project root:

```bash
cd flighthub
python -m pytest tests/ -v
```

All 25 tests should pass.

---

## Project Structure

```
flighthub/
├── backend/
│   ├── main.py          # FastAPI application entry point
│   ├── database.py      # SQLAlchemy engine + session
│   ├── models.py        # ORM models (Flight, Booking)
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── seed.py          # Database seeder with 10 sample flights
│   ├── requirements.txt
│   └── routers/
│       ├── flights.py   # GET/POST /api/flights/
│       └── bookings.py  # GET/POST/DELETE /api/bookings/
├── frontend/
│   ├── server.js        # Express static file server
│   ├── package.json
│   └── public/
│       └── index.html   # Single-page UI (vanilla JS)
└── tests/
    ├── conftest.py      # Pytest fixtures (in-memory SQLite)
    ├── test_flights.py  # 9 flight endpoint tests
    └── test_bookings.py # 16 booking endpoint tests (incl. overbooking)
```

---

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/flights/` | List / search flights |
| GET | `/api/flights/{id}` | Get single flight |
| POST | `/api/flights/` | Create a flight |
| GET | `/api/bookings/` | Search bookings by name or reference |
| GET | `/api/bookings/{ref}` | Get booking by reference |
| POST | `/api/bookings/` | Create a booking |
| DELETE | `/api/bookings/{ref}` | Cancel a booking |

---

## Assumptions

- No authentication — this is an internal staff tool
- Seat numbers follow format `<row><letter>` (e.g., `12A`, `3B`)
- Passport numbers must be alphanumeric (hyphens permitted)
- All timestamps are stored and returned in ISO 8601 format (UTC assumed)
- The database file (`flighthub.db`) is created in the `backend/` directory
