# 🩸 Recipient Waitlist Service
FastAPI + Pydantic v2  
Sprint 1 stubs (HTTP 501), OpenAPI ready.

---

## 🚀 Run

**main.py**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
open http://localhost:8000/docs
```

**Uvicorn begin（--reload）**
```bash
uvicorn main:app --reload
```

customize the server port by setting `FASTAPIPORT`, for example:
> ```bash
> FASTAPIPORT=8080 python main.py
> ```

---

## 📘 Overview
This repository implements **Microservice 2: Recipient Waitlist**, one of three services in the team’s cloud computing project:

| Service | Description |
|--------|-------------|
| MS1 – Donor Registry | Donor / Organ / Consent |
| **MS2 – Recipient Waitlist (this repo)** | **Recipient / Hospital / Need** |
| MS3 – Organ Matching & Notification | API-first with Swagger |

### Typical Flow
1. Register a **Recipient** with medical/demographic data.  
2. Record **Organ Needs** (e.g., kidney, liver) with urgency.  
3. Link the recipient to a **Hospital**.  
4. The **Matching Service (MS3)** consumes MS1 + MS2 data to match and notify.

---

## 📂 Folder Layout
```
.
├─ main.py                     # App entrypoint: create FastAPI (+ uvicorn entry)
├─ requirements.txt
├─ framework/
│  └─ app_factory.py           # App factory for consistent FastAPI creation
├─ middleware/
├─ models/
│  ├─ __init__.py
│  ├─ enums.py                 # BloodType, OrganType, UrgencyLevel, CommonStatus, NeedStatus
│  ├─ health.py                # Model for /health responses
│  ├─ recipient.py             # Recipient* (Base/Create/Read/Update)
│  ├─ hospital.py              # Hospital* (Base/Create/Read/Update)
│  └─ need.py                  # Need* (Base/Create/Read/Update)
├─ resources/
│  ├─ __init__.py              # Merge per-resource APIRouters into single `api`
│  ├─ root.py                  # GET /
│  ├─ health.py                # GET /health, GET /health/{path_echo}
│  ├─ recipients.py            # /recipients… endpoints (Sprint 1 → 501)
│  ├─ hospitals.py             # /hospitals… endpoints (Sprint 1 → 501)
│  └─ needs.py                 # /needs… endpoints (Sprint 1 → 501)
├─ services/
│  └─ __init__.py              # Business logic (CRUD/DB) → Sprint 2
├─ utils/
│  ├─ ip.py                    # Get host IP (used by /health)
│  ├─ time.py                  # UTC ISO-8601 timestamp helper
│  └─ responses.py             # `not_implemented()` → unified HTTP 501 stub
└─ requests/
   └─ smoke.http               # VS Code REST Client smoke tests
```

---

## 🧱 Layering at a glance
| Layer | Responsibility |
|---|---|
| `models/` | Input/output schemas for validation + docs |
| `resources/` | HTTP endpoints (thin controllers using APIRouter) |
| `services/` | Business logic and data persistence |
| `main.py` | App creation (+ server bootstrap with uvicorn) |

---

## 🌐 API Surface (Sprint 1 stubs)
All endpoints are defined and documented; they currently respond with **HTTP 501 Not Implemented** via `utils.responses.not_implemented()`.

### Root & Health
| Method | Path | Description |
|---|---|---|
| GET | `/` | Welcome message, link to `/docs` |
| GET | `/health` | Health check (status, timestamp, IP, optional echo) |
| GET | `/health/{path_echo}` | Health check with path echo |

### Recipients
| Method | Path | Description |
|---|---|---|
| GET | `/recipients` | List recipients (filter by status, blood type, or organ need) |
| POST | `/recipients` | Create new recipient (201) |
| GET | `/recipients/{id}` | Retrieve a recipient by ID |
| PUT | `/recipients/{id}` | Update recipient record |
| DELETE | `/recipients/{id}` | Delete recipient (204) |

### Hospitals (subresource + standalone)
| Method | Path | Description |
|---|---|---|
| GET | `/hospitals` | List all hospitals (filter by region/capacity) |
| POST | `/hospitals` | Register a new hospital (201) |
| GET | `/hospitals/{id}` | Retrieve hospital by ID |
| PUT | `/hospitals/{id}` | Update hospital info |
| DELETE | `/hospitals/{id}` | Delete hospital (204) |
| GET | `/recipients/{recipient_id}/hospital` | Get the hospital associated with a recipient |

### Needs (subresource + standalone)
| Method | Path | Description |
|---|---|---|
| GET | `/needs` | List all organ needs (filter by organ type/urgency/status) |
| POST | `/needs` | Create a new need entry (201) |
| GET | `/needs/{id}` | Retrieve a need by ID |
| PUT | `/needs/{id}` | Update need details |
| DELETE | `/needs/{id}` | Delete need (204) |
| GET | `/recipients/{recipient_id}/needs` | List needs for a recipient |
| POST | `/recipients/{recipient_id}/needs` | Add organ need for a recipient (201) |

---

## 🧩 Data Models (Pydantic v2)

### Enums (`models/enums.py`)
- **BloodType**: A+, A-, B+, B-, AB+, AB-, O+, O-  
- **OrganType**: heart, liver, kidney, lung, pancreas, intestine  
- **UrgencyLevel**: low, medium, high, critical  
- **CommonStatus**: active, inactive  
- **NeedStatus**: waiting, matched, removed

### Recipient (`models/recipient.py`)
`RecipientBase`
- full_name: str (1–200)  
- dob: date  
- blood_type: BloodType  
- status: CommonStatus = active  
- primary_hospital_id?: UUID  

`RecipientCreate` = RecipientBase  
`RecipientRead` = RecipientBase + `id`, `created_at`, `updated_at`  
`RecipientUpdate` — all fields optional

### Hospital (`models/hospital.py`)
`HospitalBase`
- name: str (1–200)  
- region: str (1–100)  
- capacity: int  

`HospitalCreate` = HospitalBase  
`HospitalRead` = HospitalBase + `id`, `created_at`, `updated_at`  
`HospitalUpdate` — all fields optional

### Need (`models/need.py`)
`NeedBase`
- organ_type: OrganType  
- urgency: UrgencyLevel = medium  
- status: NeedStatus = waiting  
- added_at?: datetime  

`NeedCreate` = NeedBase  
`NeedRead` = NeedBase + `id`, `recipient_id`, `created_at`, `updated_at`  
`NeedUpdate` — all fields optional

### Health (`models/health.py`)
- status: int  
- status_message: str  
- timestamp: str (UTC ISO-8601)  
- ip_address: str  
- echo?: str  
- path_echo?: str  

---

## 🧪 Development Tips
Run with hot-reload:
```bash
uvicorn main:app --reload
```

Smoke tests:
```bash
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/recipients   # 501 (expected in Sprint 1)
```

---

## 🗺️ Roadmap (Sprint 2+)
- Implement in-memory CRUD in `services/` and connect to endpoints.  
- Add `/health/ready` readiness check (DB ping).  
- Introduce MySQL persistence (schema aligned with enums) and load settings from `.env`.  
- Optional: CORS, request logging, typed settings.
