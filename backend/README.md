# Community Backend

This directory contains a basic FastAPI application providing a user system with JWT authentication.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. The API will be available at `http://localhost:8000/`.

The default database uses SQLite (`DATABASE_URL` environment variable can be set to a Postgres URL).
