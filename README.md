# Recipient Waitlist Service 

FastAPI + Pydantic v2. Sprint 1 **stubs** (501), OpenAPI ready, folder layout like the instructor's sample.

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# open http://localhost:8000/docs
```
## Overview

This repository implements **Microservice 2: Recipient Waitlist**, one of three services in the team project:

- **MS1 – Donor Registry** (Donor/Organ/Consent)
- **MS2 – Recipient Waitlist** (Recipient/Hospital/Need) ← this repo
- **MS3 – Matchmaking & Notification** (API‑first with Swagger)

Typical flow:
1) A **Hospital** is registered.  
2) A **Recipient** (patient) is onboarded and associated with a primary hospital.  
3) A **Need** is created for that recipient (organ type, urgency, blood type).  
4) MS3 later matches Needs with donor/organ data from MS1 and dispatches notifications.

---

## Folder Layout (teacher-style)

```
.
├─ main.py                     # App entrypoint: create FastAPI, mount all routers
├─ requirements.txt            # Pinned dependencies (same as the sprint0)
├─ framework/
│  └─ app_factory.py           # App factory: central place to create the FastAPI app
├─ middleware/
│  └─ request_logger.py        # Placeholder for future logging/tracing middleware
├─ models/
│  ├─ __init__.py              # Re-exports for convenient imports
│  ├─ enums.py                 # Shared enums (blood type, organ type, statuses)
│  ├─ health.py                # Model for /health responses
│  ├─ hospital.py              # Hospital* (Base/Create/Read/Update)
│  ├─ recipient.py             # Recipient* (Base/Create/Read/Update)
│  └─ need.py                  # Need* (Base/Create/Read/Update)
├─ resources/
│  ├─ __init__.py              # Merges per‑resource APIRouters into a single `api` router
│  ├─ root.py                  # GET /
│  ├─ health.py                # GET /health, GET /health/{path_echo}
│  ├─ hospitals.py             # /hospitals… endpoints (Sprint 1: return 501)
│  ├─ recipients.py            # /recipients… + /recipients/{id}/needs… (501)
│  └─ needs.py                 # /needs/{id}… (501)
├─ services/
│  ├─ __init__.py
│  ├─ hospitals_service.py     # Business logic lives here in Sprint 2 (CRUD/DB)
│  ├─ recipients_service.py
│  └─ needs_service.py
├─ utils/
│  ├─ __init__.py
│  ├─ ip.py                    # Helper to get host IP (used by /health)
│  ├─ time.py                  # Helper for UTC ISO-8601 timestamps (used by /health)
│  └─ responses.py             # `not_implemented()` → unified HTTP 501 stub response
└─ requests/
   └─ smoke.http               # VS Code REST Client smoke tests
```

**Layering at a glance**
- **models/** define input/output shapes (validation + documentation).
- **resources/** expose HTTP endpoints using FastAPI **APIRouter** (thin controllers).
- **services/** implement business logic and data access (to be filled in Sprint 2).
- **main.py** creates the app and mounts the merged router from `resources/__init__.py`.

---

## API Surface (Sprint 1 stubs)

> All endpoints are already defined and documented; they currently respond with **HTTP 501** via `utils.responses.not_implemented()`.

### Root & Health
- `GET /` — Welcome message, points to `/docs`.
- `GET /health` — Health check (JSON with status, timestamp, ip, optional echo).
- `GET /health/{path_echo}` — Health check with path echo (for demo/testing).

### Hospitals
- `GET /hospitals?city=&state=&status=` — List hospitals (with simple filters).
- `POST /hospitals` — Create (201).
- `GET /hospitals/{id}` — Read one.
- `PUT /hospitals/{id}` — Update.
- `DELETE /hospitals/{id}` — Delete (204).

### Recipients
- `GET /recipients?blood_type=&status=&hospital_id=` — List.
- `POST /recipients` — Create (201).
- `GET /recipients/{id}` — Read one.
- `PUT /recipients/{id}` — Update.
- `DELETE /recipients/{id}` — Delete (204).

### Needs (subresource + standalone)
- `GET /recipients/{recipient_id}/needs` — Needs of the recipient.
- `POST /recipients/{recipient_id}/needs` — Create Need for the recipient (201).
- `GET /needs/{id}` / `PUT /needs/{id}` / `DELETE /needs/{id}` — Manage a single Need.

---

## Data Models (Pydantic v2)

> Convention: **Base** = shared fields. **Create** = request body for creation. **Read** = response shape, includes read‑only fields (`id`, timestamps). **Update** = partial update (all fields optional).

### Enums (`models/enums.py`)
- **BloodType**: `A+, A-, B+, B-, AB+, AB-, O+, O-`
- **OrganType**: `heart, liver, kidney, lung, pancreas, intestine`
- **CommonStatus**: `active, inactive`
- **NeedStatus**: `waiting, matched, removed`

### Hospital (`models/hospital.py`)
- **HospitalBase**
  - `name: str` (1–200)
  - `city?: str`, `state?: str`, `phone?: str`
  - `status: CommonStatus = active`
- **HospitalCreate** = HospitalBase
- **HospitalRead** = HospitalBase + `id: UUID`, `created_at: datetime`, `updated_at: datetime`
- **HospitalUpdate** — same fields as Base, all optional

### Recipient (`models/recipient.py`)
- **RecipientBase**
  - `full_name: str` (1–200), `dob: date`, `blood_type: BloodType`
  - `status: CommonStatus = active`
  - `primary_hospital_id?: UUID`
- **RecipientCreate** = RecipientBase
- **RecipientRead** = RecipientBase + `id`, `created_at`, `updated_at`
- **RecipientUpdate** — same fields as Base, all optional

### Need (`models/need.py`)
- **NeedBase**
  - `organ_type: OrganType`
  - `urgency: int` (1–5)
  - `blood_type: BloodType`
  - `status: NeedStatus = waiting`
- **NeedCreate** = NeedBase
- **NeedRead** = NeedBase + `id: UUID`, `recipient_id: UUID`, `listed_at: datetime`, `updated_at: datetime`
- **NeedUpdate** — same fields as Base, all optional

### Health (`models/health.py`)
- `status: int`, `status_message: str`, `timestamp: str (UTC ISO-8601)`,  
  `ip_address: str`, `echo?: str`, `path_echo?: str`

---

## Development Tips

- Run with reload:
  ```bash
  uvicorn main:app --reload
  ```
- Smoke test:
  ```bash
  curl -i http://127.0.0.1:8000/health
  curl -i http://127.0.0.1:8000/hospitals   # 501 (expected in Sprint 1)
  ```
- Replace `not_implemented()` with real logic in **services/** for Sprint 2 (start with in‑memory dict, then switch to MySQL).

---

## Roadmap (Sprint 2+)

- Implement in‑memory CRUD in `services/` and wire resource handlers to services.
- Add `/health/ready` readiness check (lightweight DB ping).
- Introduce MySQL persistence (schema aligned with enums); read connection from `.env`.
- Optionally add CORS, request logging middleware, and typed settings.
