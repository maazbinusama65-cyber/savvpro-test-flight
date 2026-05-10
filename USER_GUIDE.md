# USER_GUIDE.md — FlightHub Usage Guide

## Using the Web UI

Open **http://localhost:3000** in your browser (after starting both servers).

### ✈ Flights Tab
- View all available flights on load
- Filter by **From**, **To**, or **Departure Date** and click **Search Flights**
- Click **Clear** to reset filters and show all flights
- Seats are colour-coded: green (available), amber (≤10 left), red (sold out)
- Click **Book →** on any available flight to open the booking form

### Booking a Seat
1. Fill in **Passenger Full Name**, **Passport Number**, and **Seat Number** (e.g. `12A`)
2. Click **Confirm Booking**
3. A success modal shows the unique **Booking Reference** (e.g. `FH-A3F2B1`)

### 📋 Bookings Tab
- Enter a **Passenger Name** (partial, case-insensitive) or exact **Booking Reference**
- Click **Find Bookings** to retrieve matching records
- Click **Cancel** on a confirmed booking to cancel it (frees the seat)

### 🔧 Manage Tab
- Fill in all fields to add a new flight to the system

---

## curl Examples

### List all flights
```bash
curl http://localhost:8000/api/flights/
```

### Search flights by route and date
```bash
curl "http://localhost:8000/api/flights/?origin=Karachi&destination=Lahore&departure_date=2025-08-15"
```

### Get a single flight by ID
```bash
curl http://localhost:8000/api/flights/1
```

### Create a new flight
```bash
curl -X POST http://localhost:8000/api/flights/ \
  -H "Content-Type: application/json" \
  -d '{
    "flight_number": "FH999",
    "origin": "Lahore",
    "destination": "Istanbul",
    "departure_time": "2025-09-01T22:00:00",
    "arrival_time": "2025-09-02T05:30:00",
    "price_per_seat": 95000.0,
    "total_seats": 180
  }'
```

### Book a seat
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": 1,
    "passenger_name": "Ali Hassan",
    "passport_number": "AB1234567",
    "seat_number": "12A"
  }'
```

**Example response:**
```json
{
  "id": 1,
  "reference": "FH-A3F2B1",
  "passenger_name": "Ali Hassan",
  "passport_number": "AB1234567",
  "seat_number": "12A",
  "status": "confirmed",
  "flight": {
    "id": 1,
    "flight_number": "FH101",
    "origin": "Karachi",
    "destination": "Lahore",
    "departure_time": "2025-08-15T08:00:00",
    "arrival_time": "2025-08-15T09:15:00",
    "duration_minutes": 75
  }
}
```

### Search bookings by passenger name
```bash
curl "http://localhost:8000/api/bookings/?passenger_name=Ali"
```

### Search booking by reference
```bash
curl "http://localhost:8000/api/bookings/?reference=FH-A3F2B1"
```

### Get booking by reference (direct)
```bash
curl http://localhost:8000/api/bookings/FH-A3F2B1
```

### Cancel a booking
```bash
curl -X DELETE http://localhost:8000/api/bookings/FH-A3F2B1
```

**Example response:**
```json
{
  "reference": "FH-A3F2B1",
  "status": "cancelled",
  "message": "Booking FH-A3F2B1 has been successfully cancelled. Seat 12A is now available again."
}
```

---

## Error Responses

All errors return structured JSON:

```json
{ "detail": "No seats available on this flight. Please choose a different flight." }
```

Common error codes:
- `400` — Missing required query parameters
- `404` — Flight or booking not found
- `409` — Overbooking, duplicate seat, already cancelled
- `422` — Validation error (invalid passport format, bad seat number, etc.)

---

## Interactive API Documentation

FastAPI auto-generates Swagger UI at:  
**http://localhost:8000/docs**

This lets you try all endpoints directly in the browser without curl.
