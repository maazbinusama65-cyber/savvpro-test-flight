"""
test_bookings.py — Tests for /api/bookings/ endpoints.
Includes the key business-rule test: overbooking prevention.
"""


VALID_BOOKING = {
    "passenger_name": "Maaz Bhatti",
    "passport_number": "AB1234567",
    "seat_number": "12A",
}


def make_booking(client, flight_id: int, overrides: dict = None) -> dict:
    payload = {"flight_id": flight_id, **VALID_BOOKING, **(overrides or {})}
    return client.post("/api/bookings/", json=payload)


# ── Basic CRUD ────────────────────────────────────────────────────

def test_create_booking_success(client, sample_flight):
    resp = make_booking(client, sample_flight["id"])
    assert resp.status_code == 201
    data = resp.json()
    assert data["reference"].startswith("FH-")
    assert data["status"] == "confirmed"
    assert data["passenger_name"] == "Maaz Bhatti"
    assert data["seat_number"] == "12A"


def test_booking_decrements_available_seats(client, sample_flight):
    flight_id = sample_flight["id"]
    before = client.get(f"/api/flights/{flight_id}").json()["available_seats"]
    make_booking(client, flight_id)
    after = client.get(f"/api/flights/{flight_id}").json()["available_seats"]
    assert after == before - 1


def test_booking_on_nonexistent_flight(client):
    resp = make_booking(client, flight_id=99999)
    assert resp.status_code == 404


def test_invalid_passport_rejected(client, sample_flight):
    resp = make_booking(client, sample_flight["id"], {"passport_number": "!!! bad"})
    assert resp.status_code == 422


def test_invalid_seat_format_rejected(client, sample_flight):
    resp = make_booking(client, sample_flight["id"], {"seat_number": "ABC"})
    assert resp.status_code == 422


# ── Business Rule: Overbooking ────────────────────────────────────

def test_overbooking_rejected(client):
    """
    BUSINESS RULE: A flight with 2 total seats must reject a 3rd booking.
    The 3rd request must return HTTP 409 and must not decrement seats below 0.
    """
    # Create a tiny flight (2 seats)
    flight_resp = client.post("/api/flights/", json={
        "flight_number": "TINY01",
        "origin": "Karachi",
        "destination": "Islamabad",
        "departure_time": "2025-09-01T06:00:00",
        "arrival_time":   "2025-09-01T07:20:00",
        "price_per_seat": 6000.0,
        "total_seats": 2,
    })
    assert flight_resp.status_code == 201
    fid = flight_resp.json()["id"]

    r1 = make_booking(client, fid, {"seat_number": "1A", "passport_number": "PA0000001"})
    assert r1.status_code == 201

    r2 = make_booking(client, fid, {"seat_number": "2B", "passport_number": "PA0000002"})
    assert r2.status_code == 201

    # Third booking must be rejected
    r3 = make_booking(client, fid, {"seat_number": "3C", "passport_number": "PA0000003"})
    assert r3.status_code == 409
    assert "No seats available" in r3.json()["detail"]

    # Verify seats didn't go negative
    seats = client.get(f"/api/flights/{fid}").json()["available_seats"]
    assert seats == 0


def test_duplicate_seat_rejected(client, sample_flight):
    """Two passengers cannot share the same seat on the same flight."""
    fid = sample_flight["id"]
    r1 = make_booking(client, fid, {"seat_number": "5A", "passport_number": "PA1111111"})
    assert r1.status_code == 201

    r2 = make_booking(client, fid, {"seat_number": "5A", "passport_number": "PA2222222"})
    assert r2.status_code == 409
    assert "already taken" in r2.json()["detail"]


# ── Search ────────────────────────────────────────────────────────

def test_search_by_reference(client, sample_flight):
    ref = make_booking(client, sample_flight["id"]).json()["reference"]
    resp = client.get(f"/api/bookings/?reference={ref}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["reference"] == ref


def test_search_by_passenger_name(client, sample_flight):
    make_booking(client, sample_flight["id"])
    resp = client.get("/api/bookings/?passenger_name=Maaz")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_search_no_params_rejected(client):
    resp = client.get("/api/bookings/")
    assert resp.status_code == 400


def test_get_booking_by_reference(client, sample_flight):
    ref = make_booking(client, sample_flight["id"]).json()["reference"]
    resp = client.get(f"/api/bookings/{ref}")
    assert resp.status_code == 200
    assert resp.json()["reference"] == ref


def test_get_booking_not_found(client):
    resp = client.get("/api/bookings/FH-ZZZZZZ")
    assert resp.status_code == 404


# ── Cancellation ──────────────────────────────────────────────────

def test_cancel_booking(client, sample_flight):
    fid = sample_flight["id"]
    ref = make_booking(client, fid).json()["reference"]
    seats_before = client.get(f"/api/flights/{fid}").json()["available_seats"]

    resp = client.delete(f"/api/bookings/{ref}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"

    seats_after = client.get(f"/api/flights/{fid}").json()["available_seats"]
    assert seats_after == seats_before + 1


def test_cancel_already_cancelled_booking(client, sample_flight):
    ref = make_booking(client, sample_flight["id"]).json()["reference"]
    client.delete(f"/api/bookings/{ref}")
    resp = client.delete(f"/api/bookings/{ref}")
    assert resp.status_code == 409


def test_cancel_nonexistent_booking(client):
    resp = client.delete("/api/bookings/FH-XXXXXX")
    assert resp.status_code == 404


def test_cancelled_seat_can_be_rebooked(client, sample_flight):
    """After cancellation the freed seat must be bookable again."""
    fid = sample_flight["id"]
    ref = make_booking(client, fid, {"seat_number": "7C"}).json()["reference"]
    client.delete(f"/api/bookings/{ref}")

    r2 = make_booking(client, fid, {"seat_number": "7C", "passport_number": "PB9999999"})
    assert r2.status_code == 201
