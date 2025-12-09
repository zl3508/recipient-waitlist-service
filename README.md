# 🩸 Recipient Waitlist Service
- Sprint 1
  - implemented the full API surface with 501 stubs, schema definitions, OpenAPI documentation, and routing.
- Sprint 2：
  - provided database-backed CRUD for Hospitals / Recipients / Needs,
  - connected with MySQL in VM
  - deployed on container-as-a-service using Cloud Run.

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
├─ main.py                     # FastAPI entrypoint
├─ requirements.txt
├── Dockerfile                 # Cloud Run container build
├─ framework/
│  └─ app_factory.py           
├─ middleware/
├─ models/                     # Pydantic schemas
│  ├─ __init__.py
│  ├─ enums.py                 
│  ├─ health.py                
│  ├─ recipient.py             
│  ├─ hospital.py              
│  └─ need.py                  
├─ resources/                   # API routers
│  ├─ __init__.py              
│  ├─ root.py                  
│  ├─ health.py                
│  ├─ recipients.py            
│  ├─ hospitals.py             
│  └─ needs.py                 
├─ services/                    # Business logic + DB interaction
│  ├─ __init__.py              
│  ├─ db.py                    
│  ├─ hospitals_service.py     
│  ├─ recipients_service.py    
│  └─ needs_service.py         
├─ utils/                        # Helper functions
│  ├─ ip.py                    
│  ├─ time.py                  
│  └─ responses.py             
└─ requests/                     # REST Client smoke tests
   └─ smoke.http               
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

### Recipients
| Method | Path | Description |
|---|---|---|
| GET | `/recipients` | List (filters + `limit`)`limit` defaults to 50, max 200 |
| POST | `/recipients` | Create recipient |
| GET | `/recipients/{id}` | Get recipient by ID |
| PUT | `/recipients/{id}` | Update recipient |
| DELETE | `/recipients/{id}` | Delete (blocked if needs exist) |
| GET | `/recipients/{recipient_id}/needs` | Needs for recipient |
| POST | `/recipients/{recipient_id}/needs` | Add need for recipient |

### Hospitals
| Method | Path | Description |
|---|---|---|
| GET | `/hospitals` | List (filters + `limit`) |
| POST | `/hospitals` | Create hospital |
| GET | `/hospitals/{id}` | Get hospital by ID |
| PUT | `/hospitals/{id}` | Update hospital |
| DELETE | `/hospitals/{id}` | Delete hospital |

### Needs
| Method | Path | Description |
|---|---|---|
 GET | `/needs` | List needs (filters + `limit`) |
| POST | `/needs` | Create need |
| GET | `/needs/{id}` | Get need by ID |
| PUT | `/needs/{id}` | Update need |
| DELETE | `/needs/{id}` | Delete need |
| GET | `/recipients/{recipient_id}/needs` | Needs for recipient |
| POST | `/recipients/{recipient_id}/needs` | Add need for recipient |

---

## 🧩 Data Models (Pydantic v2)

### Hospitals
| Column | Type |
|---|---|
| id | UUID |
| name | varchar(128) |
| city | varchar(64) |
| state | varchar(64) |
| phone | varchar(32) |
| status | enum('active','inactive') |
| created_at | datetime |
| updated_at | datetime |

### Recipients
| Column | Type |
|---|---|
| id | UUID |
| full_name | varchar(128) |
| dob | date |
| blood_type | enum |
| status | enum('active','inactive') |
| primary_hospital_id | FK(hospitals.id) |
| created_at | datetime |
| updated_at | datetime |

### Needs
| Column | Type |
|---|---|
| id | UUID |
| recipient_id | FK(recipients.id) |
| organ_type | enum('heart','liver','kidney','lung','pancreas','intestine') |
| urgency | tinyint unsigned CHECK 1–5 |
| blood_type | enum |
| status | enum('waiting','matched','removed') |
| listed_at | datetime |
| updated_at | datetime |

### Enums (`models/enums.py`)
- **BloodType**: A+, A-, B+, B-, AB+, AB-, O+, O-  
- **OrganType**: heart, liver, kidney, lung, pancreas, intestine  
- **CommonStatus**: active, inactive  
- **NeedStatus**: waiting, matched, removed

---

