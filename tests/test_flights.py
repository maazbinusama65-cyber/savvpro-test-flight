"""
test_flights.py — Tests for the /api/flights/ endpoints.
"""


def test_list_flights_empty(client):
    resp = client.get("/api/flights/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_flight_success(client):
    payload = {
        "flight_number": "FH001",
        "origin": "Islamabad",
        "destination": "Dubai",
        "departure_time": "2025-08-16T03:00:00",
        "arrival_time":   "2025-08-16T05:30:00",
        "price_per_seat": 32000.0,
        "total_seats": 200,
    }
    resp = client.post("/api/flights/", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["flight_number"] == "FH001"
    assert data["available_seats"] == 200
    assert data["duration_minutes"] == 150


def test_create_flight_duplicate_number(client, sample_flight):
    resp = client.post("/api/flights/", json={
        "flight_number": "TEST001",
        "origin": "Lahore",
        "destination": "Karachi",
        "departure_time": "2025-09-01T10:00:00",
        "arrival_time":   "2025-09-01T11:15:00",
        "price_per_seat": 8000.0,
        "total_seats": 100,
    })
    assert resp.status_code == 409


def test_create_flight_arrival_before_departure(client):
    resp = client.post("/api/flights/", json={
        "flight_number": "BAD001",
        "origin": "Karachi",
        "destination": "Lahore",
        "departure_time": "2025-08-16T10:00:00",
        "arrival_time":   "2025-08-16T09:00:00",   # before departure
        "price_per_seat": 5000.0,
        "total_seats": 50,
    })
    assert resp.status_code == 422


def test_get_flight_by_id(client, sample_flight):
    flight_id = sample_flight["id"]
    resp = client.get(f"/api/flights/{flight_id}")
    assert resp.status_code == 200
    assert resp.json()["flight_number"] == "TEST001"


def test_get_flight_not_found(client):
    resp = client.get("/api/flights/99999")
    assert resp.status_code == 404


def test_filter_flights_by_origin(client, sample_flight):
    resp = client.get("/api/flights/?origin=Karachi")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["origin"] == "Karachi"


def test_filter_flights_by_date(client, sample_flight):
    resp = client.get("/api/flights/?departure_date=2025-08-15")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_filter_no_match(client, sample_flight):
    resp = client.get("/api/flights/?origin=Timbuktu")
    assert resp.status_code == 200
    assert resp.json() == []
