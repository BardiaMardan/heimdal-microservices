# Heimdall Microservices

A modern AI-powered home automation orchestrator.

## Project Structure

- `backend/`: FastAPI backend with Gemini AI integration.
- `frontend/`: Next.js frontend (TypeScript, Tailwind CSS).

## Prerequisites

- Python 3.10+
- Node.js 18+
- Google AI API Key

## Getting Started

### Backend

1.  Navigate to `backend/`:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create `.env` file (copy from `.env.example`) and set `GOOGLE_AI_API_KEY`.
5.  Run the server:
    ```bash
    fastapi dev app/main.py
    ```

### Frontend

1.  Navigate to `frontend/`:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    pnpm install
    ```
3.  Create `.env.local` file (copy from `.env.local.example`).
4.  Run the development server:
    ```bash
    pnpm run dev
    ```
5.  Open [http://localhost:3000](http://localhost:3000) in your browser.

## API Documentation

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
