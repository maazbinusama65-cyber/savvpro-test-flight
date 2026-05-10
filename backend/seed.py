"""
seed.py — Populate FlightHub with realistic sample flights.
Run once:  python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from database import SessionLocal, engine, Base
import models  # noqa

Base.metadata.create_all(bind=engine)

FLIGHTS = [
    {
        "flight_number": "FH101",
        "origin": "Karachi",
        "destination": "Lahore",
        "departure_time": datetime(2025, 8, 15, 8, 0),
        "arrival_time":   datetime(2025, 8, 15, 9, 15),
        "price_per_seat": 8500.0,
        "total_seats": 120,
    },
    {
        "flight_number": "FH102",
        "origin": "Lahore",
        "destination": "Karachi",
        "departure_time": datetime(2025, 8, 15, 14, 30),
        "arrival_time":   datetime(2025, 8, 15, 15, 45),
        "price_per_seat": 8200.0,
        "total_seats": 120,
    },
    {
        "flight_number": "FH201",
        "origin": "Islamabad",
        "destination": "Dubai",
        "departure_time": datetime(2025, 8, 16, 3, 0),
        "arrival_time":   datetime(2025, 8, 16, 5, 30),
        "price_per_seat": 32000.0,
        "total_seats": 200,
    },
    {
        "flight_number": "FH202",
        "origin": "Dubai",
        "destination": "Islamabad",
        "departure_time": datetime(2025, 8, 16, 22, 15),
        "arrival_time":   datetime(2025, 8, 17, 3, 0),
        "price_per_seat": 31500.0,
        "total_seats": 200,
    },
    {
        "flight_number": "FH303",
        "origin": "Karachi",
        "destination": "London",
        "departure_time": datetime(2025, 8, 20, 1, 45),
        "arrival_time":   datetime(2025, 8, 20, 9, 0),
        "price_per_seat": 120000.0,
        "total_seats": 280,
    },
    {
        "flight_number": "FH304",
        "origin": "London",
        "destination": "Karachi",
        "departure_time": datetime(2025, 8, 22, 14, 0),
        "arrival_time":   datetime(2025, 8, 23, 4, 30),
        "price_per_seat": 118000.0,
        "total_seats": 280,
    },
    {
        "flight_number": "FH401",
        "origin": "Lahore",
        "destination": "Toronto",
        "departure_time": datetime(2025, 8, 18, 23, 55),
        "arrival_time":   datetime(2025, 8, 19, 10, 30),
        "price_per_seat": 185000.0,
        "total_seats": 250,
    },
    {
        "flight_number": "FH501",
        "origin": "Islamabad",
        "destination": "Karachi",
        "departure_time": datetime(2025, 8, 15, 11, 0),
        "arrival_time":   datetime(2025, 8, 15, 12, 20),
        "price_per_seat": 7800.0,
        "total_seats": 2,  # intentionally low to demo overbooking
    },
    {
        "flight_number": "FH601",
        "origin": "Karachi",
        "destination": "Istanbul",
        "departure_time": datetime(2025, 8, 25, 4, 30),
        "arrival_time":   datetime(2025, 8, 25, 9, 45),
        "price_per_seat": 75000.0,
        "total_seats": 180,
    },
    {
        "flight_number": "FH701",
        "origin": "Islamabad",
        "destination": "Lahore",
        "departure_time": datetime(2025, 8, 17, 7, 0),
        "arrival_time":   datetime(2025, 8, 17, 8, 0),
        "price_per_seat": 5500.0,
        "total_seats": 80,
    },
]


def seed():
    db = SessionLocal()
    try:
        for data in FLIGHTS:
            exists = db.query(models.Flight).filter(
                models.Flight.flight_number == data["flight_number"]
            ).first()
            if not exists:
                flight = models.Flight(**data, available_seats=data["total_seats"])
                db.add(flight)
        db.commit()
        print(f"✅  Seeded {len(FLIGHTS)} flights.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
