# Heimdall Orchestrator

Home automation orchestrator backend built with FastAPI.

## Phase 1 Features

- FastAPI architecture.
- JWT Authentication (In-memory storage).
- Single LLM agent endpoint (Skeleton).

## Setup

1. **Install Dependencies**

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   Copy `.env.example` to `.env` and update relevant fields.

   ```bash
   cp .env.example .env
   ```

3. **Run Application**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`
