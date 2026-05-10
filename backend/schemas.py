from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
from models import BookingStatus


# ── Flight Schemas ────────────────────────────────────────────────

class FlightBase(BaseModel):
    flight_number: str = Field(..., min_length=2, max_length=10)
    origin: str = Field(..., min_length=2, max_length=100)
    destination: str = Field(..., min_length=2, max_length=100)
    departure_time: datetime
    arrival_time: datetime
    price_per_seat: float = Field(..., gt=0)
    total_seats: int = Field(..., gt=0)

    @field_validator("arrival_time")
    @classmethod
    def arrival_after_departure(cls, v, info):
        dep = info.data.get("departure_time")
        if dep and v <= dep:
            raise ValueError("arrival_time must be after departure_time")
        return v


class FlightCreate(FlightBase):
    pass


class FlightOut(FlightBase):
    id: int
    available_seats: int
    duration_minutes: int

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_duration(cls, flight):
        data = {
            "id": flight.id,
            "flight_number": flight.flight_number,
            "origin": flight.origin,
            "destination": flight.destination,
            "departure_time": flight.departure_time,
            "arrival_time": flight.arrival_time,
            "price_per_seat": flight.price_per_seat,
            "total_seats": flight.total_seats,
            "available_seats": flight.available_seats,
            "duration_minutes": int(
                (flight.arrival_time - flight.departure_time).total_seconds() / 60
            ),
        }
        return cls(**data)


# ── Booking Schemas ───────────────────────────────────────────────

class BookingCreate(BaseModel):
    flight_id: int
    passenger_name: str = Field(..., min_length=2, max_length=200)
    passport_number: str = Field(..., min_length=5, max_length=20)
    seat_number: str = Field(..., min_length=1, max_length=6)

    @field_validator("passenger_name")
    @classmethod
    def name_must_have_space(cls, v):
        if len(v.split()) < 1:
            raise ValueError("Passenger name must include at least a first name")
        return v.strip()

    @field_validator("passport_number")
    @classmethod
    def passport_alphanumeric(cls, v):
        if not v.replace("-", "").isalnum():
            raise ValueError("Passport number must be alphanumeric")
        return v.upper()

    @field_validator("seat_number")
    @classmethod
    def seat_format(cls, v):
        v = v.upper()
        if not (v[:-1].isdigit() and v[-1].isalpha()):
            raise ValueError("Seat must be in format like 12A, 3B, 21C")
        return v


class FlightSummary(BaseModel):
    id: int
    flight_number: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int

    model_config = {"from_attributes": True}


class BookingOut(BaseModel):
    id: int
    reference: str
    passenger_name: str
    passport_number: str
    seat_number: str
    status: BookingStatus
    flight: FlightSummary

    model_config = {"from_attributes": True}


class CancelResponse(BaseModel):
    reference: str
    status: str
    message: str
