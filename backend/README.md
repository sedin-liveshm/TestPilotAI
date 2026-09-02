# TestPilot AI — Backend Service

The backend foundation for **TestPilot AI**, an AI-powered no-code Web test automation platform. Built with **FastAPI**, **Pydantic Settings**, and **Supabase**.

---

## 📋 Prerequisites

- **Python**: `3.10+` (Tested on Python `3.14.0`)
- **Supabase Account**: Project URL and API Key / Anon key

---

## 🔐 1. Supabase Project Configuration & Authentication Setup

TestPilot AI uses **Supabase Auth** for identity management and **Supabase PostgreSQL** for data storage.

### Enabled Provider
- **Email + Password**: Enable under **Supabase Dashboard -> Authentication -> Providers -> Email**.
- Custom authentication, custom JWT generation, and custom user tables are **not used**. `auth.users` is the single source of truth for identity.

---

## ⚙️ 2. Environment Variables Configuration (`.env`)

Copy the template file `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `backend/.env` with your Supabase project credentials:

```env
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_KEY=<your-supabase-anon-key>
```

> ⚠️ **Security Notice**: Never commit `.env` or hard-code Supabase credentials. `.env` is ignored by Git. Never expose `service_role` keys to client environments.

---

## 🗄️ 3. Database Migration Process

Database migrations are located in `backend/migrations/`.

### Applying Migration `001_initial_schema.sql`

To set up the base tables (`profiles`, `projects`, `tests`), foreign keys, indexes, triggers, and Row Level Security (RLS) policies:

1. Open your **Supabase Dashboard -> SQL Editor**.
2. Copy and paste the contents of [`backend/migrations/001_initial_schema.sql`](file:///c:/Users/Livesh/Desktop/TestPilot/backend/migrations/001_initial_schema.sql).
3. Click **Run**.

This migration creates:
- `public.profiles` (linked to `auth.users.id` via `ON DELETE CASCADE`)
- `public.projects` (linked to `public.profiles.id` via `ON DELETE CASCADE`)
- `public.tests` (linked to `public.projects.id` via `ON DELETE CASCADE`)
- Foreign key indexes (`idx_projects_owner_id`, `idx_tests_project_id`)
- Explicit RLS policies enforcing `auth.uid() = id`, `owner_id = auth.uid()`, and inherited project ownership.
- Automated `handle_new_user()` trigger for profile creation upon signup.

---

## 🛡️ 4. How to Test Row Level Security (RLS)

RLS test specifications are documented in [`docs/architecture/rls-test-plan.md`](file:///c:/Users/Livesh/Desktop/TestPilot/docs/architecture/rls-test-plan.md).

### Quick RLS Verification Steps
1. **Unauthenticated Query**: `SELECT * FROM projects;` -> Returns 0 rows.
2. **User A Session**: `SELECT * FROM projects;` -> Returns ONLY projects where `owner_id = User A`.
3. **User B Attempt to Access Project A**: `SELECT * FROM tests WHERE project_id = 'Project A ID';` -> Returns 0 rows.
4. **Project Spoofing Attempt**: `INSERT INTO projects (owner_id, name) VALUES ('User B ID', 'Spoof');` -> Throws RLS policy check error.

---

## 👥 5. Development User Setup & Seed Data

Sample development seeds are located in [`backend/migrations/seed.sql`](file:///c:/Users/Livesh/Desktop/TestPilot/backend/migrations/seed.sql).

### Setup Instructions
1. Register User A (`user_a@example.com`) and User B (`user_b@example.com`) in your Supabase Auth dashboard.
2. Copy their generated `UUID` values from `auth.users`.
3. Update `seed.sql` with their UUIDs and run the script in the Supabase SQL Editor.

---

## 🚀 Quickstart Setup

### 1. Create & Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run FastAPI Application

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

---

## 🧪 Running Tests

Execute unit tests using `pytest`:

```bash
pytest
```

---

## ⚠️ Common Errors & Troubleshooting

1. **`new row violates row-level security policy for table "projects"`**
   - **Cause**: Trying to insert a project with an `owner_id` that does not match `auth.uid()`.
   - **Fix**: Ensure `owner_id` equals the authenticated user's ID.

2. **`503 Service Unavailable` on `/health/db`**
   - **Cause**: Invalid or placeholder `SUPABASE_URL` in `.env`.
   - **Fix**: Update `backend/.env` with your active Supabase URL & API key.

3. **Foreign key constraint violation on `profiles`**
   - **Cause**: Attempting to insert a profile for a non-existent `auth.users` ID.
   - **Fix**: User must register in Supabase Auth first before inserting profile.

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
├── migrations/
│   ├── 001_initial_schema.sql  # Database schema & RLS policies
│   └── seed.sql                # Development seed instructions & sample data
│
├── tests/
│   ├── __init__.py
│   └── test_health.py   # Health endpoint unit tests
│
├── .env.example         # Environment template
├── .env                 # Local secrets (gitignored)
├── .gitignore           # Backend gitignore
├── requirements.txt     # Python dependencies
└── README.md            # Onboarding & database documentation
```
