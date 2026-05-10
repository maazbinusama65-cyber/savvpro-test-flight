from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from database import get_db
import models
import schemas

router = APIRouter()


def _generate_reference() -> str:
    """Generate a short, unique booking reference like FH-A3F2B1."""
    return "FH-" + uuid.uuid4().hex[:6].upper()


def _seat_taken(db: Session, flight_id: int, seat_number: str) -> bool:
    return db.query(models.Booking).filter(
        models.Booking.flight_id == flight_id,
        models.Booking.seat_number == seat_number,
        models.Booking.status == models.BookingStatus.confirmed,
    ).first() is not None


@router.post("/", response_model=schemas.BookingOut, status_code=201, summary="Book a seat")
def create_booking(payload: schemas.BookingCreate, db: Session = Depends(get_db)):
    """
    Book a seat on a flight.

    Overbooking rule (documented in ARCHITECTURE.md):
    - If available_seats == 0 the request is rejected with HTTP 409.
    - Seat availability is decremented atomically within the same transaction
      so two simultaneous requests cannot both claim the last seat.
    - If the requested seat number is already taken (by a confirmed booking)
      the request is rejected with HTTP 409 and the passenger is asked to
      choose a different seat.
    """
    # Lock the flight row for the duration of this transaction
    flight = (
        db.query(models.Flight)
        .filter(models.Flight.id == payload.flight_id)
        .with_for_update()
        .first()
    )
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    if flight.available_seats <= 0:
        raise HTTPException(
            status_code=409,
            detail="No seats available on this flight. Please choose a different flight.",
        )

    if _seat_taken(db, flight.id, payload.seat_number):
        raise HTTPException(
            status_code=409,
            detail=f"Seat {payload.seat_number} is already taken. Please choose a different seat.",
        )

    # Generate a unique reference (retry on the rare collision)
    for _ in range(5):
        ref = _generate_reference()
        if not db.query(models.Booking).filter(models.Booking.reference == ref).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate a unique booking reference")

    booking = models.Booking(
        reference=ref,
        flight_id=flight.id,
        passenger_name=payload.passenger_name,
        passport_number=payload.passport_number,
        seat_number=payload.seat_number,
        status=models.BookingStatus.confirmed,
    )
    flight.available_seats -= 1

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return _booking_out(booking)


@router.get("/", response_model=list[schemas.BookingOut], summary="Search bookings")
def search_bookings(
    passenger_name: Optional[str] = Query(None, description="Filter by passenger name (partial match)"),
    reference: Optional[str] = Query(None, description="Filter by exact booking reference"),
    db: Session = Depends(get_db),
):
    """
    Retrieve bookings by passenger name (partial, case-insensitive) or
    by exact booking reference.  At least one filter must be provided.
    """
    if not passenger_name and not reference:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one query parameter: passenger_name or reference",
        )

    q = db.query(models.Booking)

    if reference:
        q = q.filter(models.Booking.reference == reference.upper())
    if passenger_name:
        q = q.filter(models.Booking.passenger_name.ilike(f"%{passenger_name}%"))

    bookings = q.order_by(models.Booking.id.desc()).all()
    return [_booking_out(b) for b in bookings]


@router.get("/{reference}", response_model=schemas.BookingOut, summary="Get booking by reference")
def get_booking(reference: str, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(
        models.Booking.reference == reference.upper()
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return _booking_out(booking)


@router.delete("/{reference}", response_model=schemas.CancelResponse, summary="Cancel a booking")
def cancel_booking(reference: str, db: Session = Depends(get_db)):
    """
    Cancel a booking by its reference code.
    - Already-cancelled bookings return 409.
    - Cancellation restores one seat on the flight.
    """
    booking = (
        db.query(models.Booking)
        .filter(models.Booking.reference == reference.upper())
        .with_for_update()
        .first()
    )
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status == models.BookingStatus.cancelled:
        raise HTTPException(status_code=409, detail="Booking is already cancelled")

    booking.status = models.BookingStatus.cancelled
    booking.flight.available_seats += 1

    db.commit()
    return schemas.CancelResponse(
        reference=booking.reference,
        status="cancelled",
        message=f"Booking {booking.reference} has been successfully cancelled. Seat {booking.seat_number} is now available again.",
    )


# ── Helper ────────────────────────────────────────────────────────

def _booking_out(booking: models.Booking) -> schemas.BookingOut:
    flight = booking.flight
    duration = int((flight.arrival_time - flight.departure_time).total_seconds() / 60)
    flight_summary = schemas.FlightSummary(
        id=flight.id,
        flight_number=flight.flight_number,
        origin=flight.origin,
        destination=flight.destination,
        departure_time=flight.departure_time,
        arrival_time=flight.arrival_time,
        duration_minutes=duration,
    )
    return schemas.BookingOut(
        id=booking.id,
        reference=booking.reference,
        passenger_name=booking.passenger_name,
        passport_number=booking.passport_number,
        seat_number=booking.seat_number,
        status=booking.status,
        flight=flight_summary,
    )
