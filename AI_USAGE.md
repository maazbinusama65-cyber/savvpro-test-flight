# AI_USAGE.md — AI Coding Agent Usage Log

## Tool Used

**Claude Sonnet (claude.ai)** — used as the primary AI coding agent throughout this assessment.

---

## How Claude Was Used

Claude was given the full TASK.md assessment brief and asked to build the entire FlightHub application from scratch, including:

- Backend architecture (FastAPI, SQLAlchemy models, Pydantic schemas, routers)
- Overbooking business logic
- Full test suite (25 tests)
- Express.js frontend server
- Single-page HTML/CSS/JS UI
- All documentation files

---

## Key Prompts

### 1. Project Architecture
> "Build a full-stack flight search and booking system. Backend: Python FastAPI. Frontend: Node.js Express. Database: SQLite. Follow the spec in TASK.md exactly."

**What Claude generated:** Project folder structure, SQLAlchemy models, Pydantic schemas, FastAPI routers with CORS, seed script.

---

### 2. Overbooking Decision
> "The spec says 'handle overbooking appropriately'. What approach should I use and how should you implement it?"

**What Claude generated:** Row-level locking with `SELECT … FOR UPDATE`, hard 409 rejection when seats hit zero, with an explanation of why silent waitlisting would be worse for a travel agency context.

---

### 3. Test Infrastructure
> "The tests fail because the in-memory SQLite database isn't shared between threads. Fix conftest.py."

**What happened:** Claude initially generated a conftest that failed because FastAPI's TestClient runs the app in a worker thread, and SQLite in-memory databases are per-connection by default. Claude identified the fix (SQLAlchemy `StaticPool`) and corrected the conftest.

---

### 4. Frontend UI
> "Build a dark-themed single-page HTML UI for travel agency staff. Include flight search, booking modal, booking lookup, and cancellation. All in one file."

**What Claude generated:** Complete `index.html` with Syne + DM Sans fonts, dark design system, vanilla JS consuming the FastAPI endpoints, booking modal with confirmation reference display.

---

## What Claude Got Wrong (and How It Was Corrected)

### Issue 1: Test database isolation
**Problem:** Claude's initial conftest used a regular `create_engine("sqlite:///:memory:")` without `StaticPool`. This caused `no such table` errors in tests because the TestClient's worker thread opened a different connection to the in-memory database than the one where tables were created.

**Fix:** Claude self-identified the issue when shown the error output and corrected it by adding `poolclass=StaticPool` to share a single connection across all threads in the test session.

### Issue 2: Module import ordering in tests
**Problem:** FastAPI calls `Base.metadata.create_all(bind=engine)` at module import time. If `conftest.py` imports `database` after patching the engine reference, the wrong engine gets used.

**Fix:** Claude restructured conftest.py to patch `database.engine` before importing `main`, ensuring the startup `create_all` call targets the test engine.

---

## Overall Assessment of AI Tool Quality

Claude was highly effective for this task:
- Generated production-quality FastAPI code with appropriate use of `with_for_update()`, Pydantic validators, and SQLAlchemy relationships
- Made thoughtful decisions on the deliberate ambiguities (overbooking → hard reject with explanation)
- Self-corrected test infrastructure bugs when shown the error output
- Produced coherent documentation without hallucinating API details

The main limitation: Claude cannot run code interactively, so testing/debugging required iterating on error output manually. However, when given clear error messages, it diagnosed and fixed issues in one or two turns.
