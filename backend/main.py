from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models  # noqa: F401 — registers models with Base

from routers import flights, bookings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FlightHub API",
    description="Flight search and booking system for travel agency staff",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flights.router, prefix="/api/flights", tags=["Flights"])
app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])


@app.get("/")
def root():
    return {"message": "FlightHub API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
