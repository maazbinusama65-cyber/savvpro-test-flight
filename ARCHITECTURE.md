# ARCHITECTURE.md — FlightHub Design Decisions

## Data Model

### `flights` table

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| flight_number | TEXT UNIQUE | e.g. `FH101` |
| origin | TEXT | City name |
| destination | TEXT | City name |
| departure_time | DATETIME | ISO 8601 |
| arrival_time | DATETIME | ISO 8601 |
| price_per_seat | REAL | In PKR |
| total_seats | INTEGER | Fixed at creation |
| available_seats | INTEGER | Decremented on booking, restored on cancellation |

### `bookings` table

| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| reference | TEXT UNIQUE | `FH-` + 6 hex chars (e.g. `FH-A3F2B1`) |
| flight_id | INTEGER FK → flights | |
| passenger_name | TEXT | |
| passport_number | TEXT | Stored uppercase |
| seat_number | TEXT | Stored uppercase, e.g. `12A` |
| status | ENUM | `confirmed` \| `cancelled` |

---

## API Design

REST conventions:
- Resources are nouns: `/api/flights/`, `/api/bookings/`
- `GET` for reads, `POST` for creates, `DELETE` for cancellation
- `DELETE /api/bookings/{ref}` performs a **soft delete** (status → `cancelled`), not a physical row removal. This preserves audit history.

All responses return appropriate HTTP status codes:
- `200 OK` — successful read / cancellation
- `201 Created` — successful flight creation or booking
- `400 Bad Request` — missing required query params
- `404 Not Found` — resource not found
- `409 Conflict` — overbooking, duplicate seat, duplicate flight number, or double-cancellation
- `422 Unprocessable Entity` — Pydantic validation failure (FastAPI default)

---

## Ambiguity Resolutions

### 1. "Handle overbooking appropriately"

**Decision: Hard reject (HTTP 409) when `available_seats == 0`.**

Reasoning:
- A travel agency has a duty to sell only real seats. Silent waitlisting would surprise the passenger later.
- The booking endpoint acquires a `SELECT … FOR UPDATE` row-level lock on the flight row, so two simultaneous requests cannot both claim the last seat.
- If the requested **seat number** is already taken by a confirmed booking, the request is also rejected with HTTP 409 and a message asking the agent to choose a different seat.
- After cancellation, `available_seats` is restored, so the freed seat can be rebooked.

### 2. "Display relevant flight information"

**Decision: Prioritise the agent workflow.**

The UI is designed for travel agency staff, not end consumers. The information hierarchy is:

1. **Route** (origin → destination) — the first thing an agent needs to scan
2. **Departure datetime + duration** — scheduling context
3. **Available seats** — colour-coded badge (green / amber / red) so agents can spot near-full flights at a glance
4. **Price** — displayed prominently but not dominant; agents often have the price pre-agreed

Secondary information (arrival time, flight number) is shown in smaller text. The "Book" button is suppressed on sold-out flights and replaced with a "Sold Out" badge.

---

## Technology Choices

| Layer | Choice | Rationale |
|---|---|---|
| Backend framework | FastAPI | Fast, async-ready, Pydantic built-in, auto-docs |
| ORM | SQLAlchemy 2 | Mature, type-safe, supports row-level locking |
| Database | SQLite | Zero-config, sufficient for a single-staff internal tool |
| Frontend server | Express.js | Minimal static-file server as required |
| Frontend UI | Vanilla JS + HTML/CSS | No build step; works immediately |
| Test framework | pytest + FastAPI TestClient | Industry standard; isolated in-memory DB per test |

---

## Testing Strategy

Tests use SQLAlchemy's `StaticPool` to share a single in-memory SQLite connection across threads (the FastAPI test client runs in a worker thread). Each test function gets a fresh schema via `create_all` / `drop_all`.

Test categories:
- **Unit-level API tests** — happy path and error cases for every endpoint
- **Business rule test** — `test_overbooking_rejected` explicitly verifies the core invariant: `available_seats` never goes below zero
- **State transition tests** — cancellation restores seats; cancelled seat can be rebooked
