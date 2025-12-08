# 🩸 Recipient Waitlist Service
- Sprint 1 implemented the full API surface with 501 stubs, schema definitions, OpenAPI documentation, and routing.
- Sprint 2 provided database-backed CRUD for Hospitals / Recipients / Needs, connected with MySQL in VM and deployed on container-as-a-service using Cloud Run.

---

## 🚀 Run
```
# local
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python main.py
open http://localhost:8000/docs

# docker related
docker build --platform linux/amd64 -t zhenqili/recipient-waitlist-service:latest .
docker push zhenqili/recipient-waitlist-service:latest

# cloud run 
gcloud run deploy recipient-waitlist-service \
  --image docker.io/zhenqili/recipient-waitlist-service:latest \
  --platform managed \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars DB_HOST="35.232.73.84",DB_PORT="3306",DB_USER="appuser",DB_PASSWORD="password123",DB_NAME="microservice_db"
```

---

## 📘 Overview
This repository implements **Microservice 2: Recipient Waitlist**, one of three services in the team’s cloud computing project:

| Service | Description |
|--------|-------------|
| MS1 – Donor Registry | Donor / Organ / Consent |
| **MS2 – Recipient Waitlist (this repo)** | **Recipient / Hospital / Need** |
| MS3 – Organ Matching & Notification | API-first with Swagger |

### Typical Flow (Hospital → Recipient → Needs → Matching)
This microservice models a simple hierarchy:

- One **hospital** can have many **recipients**.
- One **recipient** can have many **needs**.
- The hierarchy is enforced by foreign keys so that you must always clean up the lower level before deleting the upper level.

### 1) Hospital onboarding and invariants

- Clients create the hospital first (if it does not already exist).
- Each hospital gets a stable identifier that can be referenced by recipients.
- A hospital can have zero or more recipients.
- Deletion rule: a hospital **cannot** be deleted if there are recipients that still reference it.  
  Callers must first delete or reassign those recipients before deleting the hospital.

### 2) Recipient onboarding and invariants

- The care team creates a recipient; associating a hospital is **optional**:
  - `primary_hospital_id` may be omitted (recipient has no primary hospital yet), or
  - it must point to an existing hospital.
- The service validates that any provided `primary_hospital_id` is valid; an incorrect / non-existent hospital ID is rejected.
- New recipients are created with `status = active`.
- A recipient can have zero or more needs.
- Deletion rule: a recipient **cannot** be deleted if there are needs that still reference it.  
  Callers must delete the recipient’s needs before deleting the recipient.

### 3) Recording and maintaining organ needs

- A need can only be created for an **existing recipient** (enforced by the `/recipients/{recipient_id}/needs` routes).
- Each need captures one organ (`organ_type`), an urgency level (1–5), and the recipient’s compatible `blood_type`.
- Need defaults: `status = waiting`, with `listed_at` auto-set.
- Multiple needs can be open for the same recipient; urgency and status may change over time.
- If a need stores a hospital reference (or derives it from the recipient), any provided hospital ID must also refer to a valid hospital; invalid IDs are rejected by the service.

### 4) Data quality and lifecycle rules

- The hierarchy is strictly **top-down for creation** (Hospital → Recipient → Needs), and **bottom-up for deletion** (Needs → Recipient → Hospital).
- Database foreign keys and API-level validation are used together to prevent orphaned data:
  - You cannot delete a **recipient** that still has needs.
  - You cannot delete a **hospital** that still has recipients.
- Callers are expected to follow the sequence:
  1. Delete or close needs,
  2. Delete the recipient,
  3. Finally, delete the hospital (if desired).

### 5) Matching and consumption (handled in MS3)

- MS3 queries `/needs` or `/recipients/{recipient_id}/needs` to find open requests.
- When a match is made (using MS1 donors/organs), MS3 updates or deletes the matched need to prevent reuse (implementation happens outside this repo).
- After consumption, the need should move to `status = matched` or be removed, ensuring that a single organ is not matched twice.
---

## 📂 Folder Layout
```
.
├─ main.py                     # App entrypoint: create FastAPI (+ uvicorn entry)
├─ requirements.txt
├── Dockerfile                 # Cloud Run container build
├─ framework/
│  └─ app_factory.py           # App factory for consistent FastAPI creation
├─ middleware/
├─ models/
│  ├─ __init__.py
│  ├─ enums.py                 # BloodType, OrganType, CommonStatus, NeedStatus
│  ├─ health.py                # Model for /health responses
│  ├─ recipient.py             # Recipient* (Base/Create/Read/Update)
│  ├─ hospital.py              # Hospital* (Base/Create/Read/Update)
│  └─ need.py                  # Need* (Base/Create/Read/Update)
├─ resources/
│  ├─ __init__.py              # Merge per-resource APIRouters into single `api`
│  ├─ root.py                  # GET /
│  ├─ health.py                # GET /health, GET /health/{path_echo}
│  ├─ recipients.py            # /recipients… endpoints API routes → services
│  ├─ hospitals.py             # /hospitals… endpoints API routes → services
│  └─ needs.py                 # /needs… endpoints API routes → services
├─ services/
│  ├─ __init__.py              # Package marker; logic lives in the modules below
│  ├─ db.py                    # lical test + VM with MySQL
│  ├─ hospitals_service.py     # DB CRUD
│  ├─ recipients_service.py    # DB CRUD
│  └─ needs_service.py         # DB CRUD
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
| `models/` | Pydantic v2 schemas for request/response validation and OpenAPI docs |
| `resources/` | FastAPI `APIRouter` modules defining REST endpoints (async) |
| `services/` | Business logic + MySQL CRUD via `mysql-connector-python`; light domain validation |
| `services/db.py` | Connection factory + context manager for MySQL (Cloud Run socket or TCP) |
| `utils/` | IP/time helpers and shared response helpers |
| `main.py` | Application factory wiring: create app, mount routers, Cloud Run friendly |

### Sprint 2 Enhancements
- ✅ MySQL-backed persistence through `services/db.py`
- ✅ Full CRUD for hospitals, recipients, and needs (with nested routes)
- ✅ Async FastAPI routers delegating to service layer
- ✅ Basic domain validation (e.g., recipient must exist before adding needs)
- ✅ `limit` query caps on collection endpoints (no offset/cursor pagination)
- ⚠️ Not implemented: ETags, HATEOAS links, 201 Location headers, or 202/polling flows

---

## 🌐 API Surface

### Root & Health
| Method | Path | Description |
|---|---|---|
| GET | `/` | Welcome message, link to `/docs` |
| GET | `/health` | Health check (status, timestamp, IP, optional echo) |
| GET | `/health/{path_echo}` | Health check with path echo |
| GET | `/db-test-ms2` | NEW (Sprint 2) Verifies Cloud SQL connectivity (SELECT DATABASE() returns service_b_db) |

### Recipients
| Method | Path | Description |
|---|---|---|
| GET | `/recipients` | List recipients (filter by status, blood type, or hospital; `limit` defaults to 50, max 200; no offset/cursor pagination) |
| POST | `/recipients` | Create a new recipient (201). primary_hospital_id` is stored but not enforced by a DB foreign key in code.  |
| GET | `/recipients/{id}` | Retrieve recipient by UUID |
| PUT | `/recipients/{id}` | Update any recipient field (all fields optional) |
| DELETE | `/recipients/{id}` | Delete recipient (204); if the recipient has no needs → ✔️ delete; if needs exist → ❌ FK violation → 500 (recipient not deleted) |
| GET | `/recipients/{recipient_id}/needs` | List all needs belonging to the recipient |
| POST | `/recipients/{recipient_id}/needs` | Create an organ need under this recipient (201) |

### Hospitals (subresource + standalone)
| Method | Path | Description |
|---|---|---|
| GET | `/hospitals` | List all hospitals (filter by id, name, city, state, phone, status) `limit` defaults to 50, max 200; |
| POST | `/hospitals` | Register a new hospital (201) |
| GET | `/hospitals/{id}` | Retrieve hospital by ID |
| PUT | `/hospitals/{id}` | Update hospital info |
| DELETE | `/hospitals/{id}` | Delete hospital (204) |
| GET | `/recipients/{recipient_id}/hospital` | Get the hospital associated with a recipient |

### Needs (subresource + standalone)
| Method | Path | Description |
|---|---|---|
| GET | `/needs` | List all organ needs (filter by organ_type, urgency, blood_type, status |
| POST | `/needs` | Create a new need entry (201) |
| GET | `/needs/{id}` | Retrieve a need by ID |
| PUT | `/needs/{id}` | Update organ need (organ, urgency 1–5, blood type, status) |
| DELETE | `/needs/{id}` | Delete need (204) |
| GET | `/recipients/{recipient_id}/needs` | List needs for a recipient |
| POST | `/recipients/{recipient_id}/needs` | Add organ need for a recipient (201) |

---

## 🧩 Data Models (Pydantic v2)

### Enums (`models/enums.py`)
- **BloodType**: A+, A-, B+, B-, AB+, AB-, O+, O-  
- **OrganType**: heart, liver, kidney, lung, pancreas, intestine  
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
- `name: str (1–200)`
- `city: str (1–100)`
- `state: str (2)`  <!-- e.g., NY, CA -->
- `phone: str (E.164 recommended)`
- `status: CommonStatus = active`  <!-- active | inactive -->

`HospitalCreate` = HospitalBase  
`HospitalRead` = HospitalBase + `id`, `created_at`, `updated_at`  
`HospitalUpdate` — all fields optional

### Need (`models/need.py`)
`NeedBase`
- organ_type: OrganType  
- urgency: int (1–5)  
- blood_type: BloodType  
- status: NeedStatus = waiting  

`NeedCreate` = NeedBase  
`NeedRead` = NeedBase + `id: UUID`, `recipient_id`, `listed_at`, `updated_at`  
`NeedUpdate` — all fields optional

### Health (`models/health.py`)
- status: int  
- status_message: str  
- timestamp: str (UTC ISO-8601)  
- ip_address: str  
- echo?: str  
- path_echo?: str  

---
## 🧪 Service Logic (Sprint 2)
**Hospitals Service**
- list (with filters and limit)
- create / update / delete
- timestamp management
- status enum mapping
- delete behavior:
  - hospital is not referenced by any recipients → ✔️ deleted successfully
  - some recipients have `primary_hospital_id = {id}` → ❌ MySQL FK violation → 500 error (no rows deleted)

**Recipients Service**
- list all recipients with filters (`blood_type`, `status`, `hospital_id`, `limit`)
- create a new recipient with optional primary_hospital_id  
  - primary_hospital_id empty/null → ✔️ success  
  - primary_hospital_id does not exist → ❌ MySQL FK violation → 500  
- get / update / delete a single recipient (`GET/PUT/DELETE /recipients/{id}`)
- update logic performs partial updates: fields omitted in the request retain their previous values
- manage `created_at` / `updated_at` timestamps in the service layer
- delete behavior: deletes row when found (204) or returns 404
- exposes subresource for needs:
  - `GET /recipients/{recipient_id}/needs`
  - `POST /recipients/{recipient_id}/needs`
  
**Needs Service**
- list all needs with filters (`organ_type`, `status`, `recipient_id`, `limit`)
- create a new need under a recipient (`POST /recipients/{recipient_id}/needs`); the route validates recipient existence before invoking the service  
- get / update / delete a single need (`GET/PUT/DELETE /needs/{id}`)
- enforce urgency constraints (1–5) and status enum (`waiting/matched/removed`)
- manage `listed_at` / `updated_at` timestamps in the service layer
- deletion behavior:
  - need with valid id → ✔️ deleted successfully  
  - no cascade: deleting a recipient with remaining needs → ❌ blocked by FK constraint

**Notes**
- MySQL FK constraints block deletion of a parent row when it still has children.
- To safely delete:
  - delete **needs → then recipient**
  - update/remove **recipients → then hospital**

---
## Database Model
### Table Cheat Sheet
| Table | Key Columns | Notes |
|---|---|---|
| `hospitals` | `id` (UUID), `name`, `city`, `state`, `phone`, `status`, timestamps | Status controls active/inactive visibility. |
| `recipients` | `id` (UUID), `full_name`, `dob`, `blood_type`, `status`, `primary_hospital_id`, timestamps | FK to `hospitals.id` but cascades depend on DB config. |
| `needs` | `id` (UUID), `recipient_id` (FK), `organ_type`, `urgency` (1–5), `blood_type`, `status`, timestamps | Urgency checked 1–5; FK must point to existing recipient. |

### Table Model (MS2)
| Table | Column | Type |
|---|---|---|
| `hospitals` | id | UUID |
|  | name | varchar(128) |
|  | city | varchar(64) |
|  | state | varchar(64) |
|  | phone | varchar(32) |
|  | status | enum('active','inactive') |
|  | created_at | timestamp |
|  | updated_at | timestamp |
| `recipients` | id | UUID |
|  | full_name | varchar(128) |
|  | dob | date |
|  | blood_type | enum |
|  | status | enum('active','inactive') |
|  | primary_hospital_id | FK(hospitals.id) |
|  | created_at | timestamp |
|  | updated_at | timestamp |
| `needs` | id | UUID |
|  | recipient_id | FK(recipients.id) |
|  | organ_type | enum('heart','liver','kidney','lung','pancreas','intestine') |
|  | urgency | tinyint unsigned CHECK 1–5 |
|  | blood_type | enum |
|  | status | enum('waiting','matched','removed') |
|  | listed_at | timestamp |
|  | updated_at | timestamp |



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

