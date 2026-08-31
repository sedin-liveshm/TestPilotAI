# TestPilot AI — Backend Service

The backend foundation for **TestPilot AI**, an AI-powered no-code Web test automation platform. Built with **FastAPI**, **Pydantic Settings**, and **Supabase**.

---

## 📋 Prerequisites

- **Python**: `3.10+` (Tested on Python `3.14.0`)
- **Supabase Account**: Project URL and API Key / Anon key

---

## 🚀 Quickstart Setup

### 1. Navigate to backend directory

```bash
cd backend
```

### 2. Create Virtual Environment

**Windows (PowerShell / CMD):**
```powershell
python -m venv .venv
```

**macOS / Linux:**
```bash
python3 -m venv .venv
```

---

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\.venv\Scripts\activate
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source .venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Configure Environment Variables (`.env`)

Copy the template file `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and fill in your Supabase credentials:

```env
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_KEY=<your-supabase-anon-key>
```

> **Note**: Never commit `.env` to Git repository. `.env` is listed in `.gitignore`.

---

## 🏃 Running the Application

Start the FastAPI development server with auto-reload:

```bash
uvicorn app.main:app --reload
```

Server will start on `http://127.0.0.1:8000`.

---

## 📍 API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | `GET` | Basic backend process health check |
| `/health/db` | `GET` | Supabase database connectivity check |
| `/docs` | `GET` | Interactive Swagger API documentation |
| `/redoc` | `GET` | ReDoc API documentation |

### Health Check Example

```bash
curl http://127.0.0.1:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "testpilot-backend"
}
```

### Database Connectivity Check Example

```bash
curl http://127.0.0.1:8000/health/db
```

**Response:**
```json
{
  "status": "ok",
  "database": "connected"
}
```

---

## 🧪 Running Tests

Execute unit and integration tests using `pytest`:

```bash
pytest
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application & health routes
│   ├── config.py        # Centralized Pydantic Settings configuration
│   └── db/
│       ├── __init__.py
│       └── supabase.py  # Supabase client singleton
│
├── tests/
│   ├── __init__.py
│   └── test_health.py   # Health endpoint unit tests
│
├── .env.example         # Environment template
├── .env                 # Local secrets (gitignored)
├── .gitignore           # Backend gitignore
├── requirements.txt     # Python dependencies
└── README.md            # Onboarding documentation
```
