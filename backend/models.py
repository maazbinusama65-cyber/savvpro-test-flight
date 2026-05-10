from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class BookingStatus(str, enum.Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"


class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String, unique=True, nullable=False, index=True)
    origin = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False, index=True)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    price_per_seat = Column(Float, nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)

    bookings = relationship("Booking", back_populates="flight")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String, unique=True, nullable=False, index=True)
    flight_id = Column(Integer, ForeignKey("flights.id"), nullable=False)
    passenger_name = Column(String, nullable=False, index=True)
    passport_number = Column(String, nullable=False)
    seat_number = Column(String, nullable=False)
    status = Column(SAEnum(BookingStatus), default=BookingStatus.confirmed, nullable=False)

    flight = relationship("Flight", back_populates="bookings")
