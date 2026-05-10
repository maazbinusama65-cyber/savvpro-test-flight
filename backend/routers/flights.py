from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import date

from database import get_db
import models
import schemas

router = APIRouter()


@router.get("/", response_model=list[schemas.FlightOut], summary="List all flights")
def list_flights(
    origin: Optional[str] = Query(None, description="Filter by origin city"),
    destination: Optional[str] = Query(None, description="Filter by destination city"),
    departure_date: Optional[date] = Query(None, description="Filter by departure date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Return all available flights, optionally filtered by origin, destination,
    and/or departure date.  Only flights with at least one available seat
    are returned unless all three filters are omitted (staff may still want
    to see sold-out flights in the unfiltered list for scheduling reference).
    """
    q = db.query(models.Flight)

    if origin:
        q = q.filter(func.lower(models.Flight.origin) == origin.lower().strip())
    if destination:
        q = q.filter(func.lower(models.Flight.destination) == destination.lower().strip())
    if departure_date:
        q = q.filter(func.date(models.Flight.departure_time) == departure_date)

    flights = q.order_by(models.Flight.departure_time).all()

    if not flights:
        return []

    return [schemas.FlightOut.from_orm_with_duration(f) for f in flights]


@router.get("/{flight_id}", response_model=schemas.FlightOut, summary="Get a single flight")
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    flight = db.query(models.Flight).filter(models.Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return schemas.FlightOut.from_orm_with_duration(flight)


@router.post("/", response_model=schemas.FlightOut, status_code=201, summary="Create a flight (admin)")
def create_flight(payload: schemas.FlightCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Flight).filter(
        models.Flight.flight_number == payload.flight_number
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Flight number already exists")

    flight = models.Flight(
        **payload.model_dump(),
        available_seats=payload.total_seats,
    )
    db.add(flight)
    db.commit()
    db.refresh(flight)
    return schemas.FlightOut.from_orm_with_duration(flight)
