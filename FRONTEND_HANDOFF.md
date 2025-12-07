# Frontend Handoff – Recipient Waitlist Service (MS2)

Use this as the quick reference for connecting a browser UI to MS2.

## Base URLs
- **Local dev**: `http://localhost:8000`
- **Cloud Run (example)**: `https://recipient-waitlist-service-<hash>-ue.a.run.app`
- OpenAPI docs: `GET /docs`

> There is no authentication layer yet; all endpoints are open.

## Core Resources
All requests/response bodies are JSON.

### Recipients
- `GET /recipients` — list (query params: `status`, `blood_type`, `organ_type`, `limit`)
- `POST /recipients` — create (201). Body: `{ "full_name", "dob", "blood_type", "status?", "primary_hospital_id?" }`
- `GET /recipients/{id}` — fetch one
- `PUT /recipients/{id}` — update (partial fields allowed)
- `DELETE /recipients/{id}` — delete (204)
- `GET /recipients/{id}/needs` — list needs for recipient
- `POST /recipients/{id}/needs` — create a need for that recipient (201)

### Hospitals
- `GET /hospitals` — list (filters: `id`, `name`, `city`, `state`, `phone`, `status`)
- `POST /hospitals` — create (201). Body: `{ "name", "city", "state", "phone", "status?" }`
- `GET /hospitals/{id}` — fetch one
- `PUT /hospitals/{id}` — update
- `DELETE /hospitals/{id}` — delete (204)
- `GET /recipients/{recipient_id}/hospital` — recipient’s hospital link

### Needs
- `GET /needs` — list (filters: `organ_type`, `urgency`, `blood_type`, `status`)
- `POST /needs` — create (201). Body: `{ "organ_type", "urgency", "blood_type", "status?", "recipient_id" }`
- `GET /needs/{id}` — fetch one
- `PUT /needs/{id}` — update
- `DELETE /needs/{id}` — delete (204)

## Sample Calls
```http
# create hospital
POST {{BASE_URL}}/hospitals
Content-Type: application/json

{
  "name": "General",
  "city": "NYC",
  "state": "NY",
  "phone": "+12125551234"
}
```

```http
# create recipient linked to hospital
POST {{BASE_URL}}/recipients
Content-Type: application/json

{
  "full_name": "Ada Lovelace",
  "dob": "1990-12-10",
  "blood_type": "O+",
  "primary_hospital_id": "<hospital-uuid>"
}
```

```http
# add an organ need for that recipient
POST {{BASE_URL}}/recipients/{{recipientId}}/needs
Content-Type: application/json

{
  "organ_type": "kidney",
  "urgency": 4,
  "blood_type": "O+"
}
```

## Notes for the UI team
- Prefer the nested routes (`/recipients/{id}/needs`, `/recipients/{id}/hospital`) to navigate relationships from the UI.
- Pagination is a simple `limit` query param; no cursor/offset yet.
- CORS is **not** configured here. If the web app is served from a different origin, proxy through a backend/API gateway or add CORS middleware when deploying.
- `dob` expects `YYYY-MM-DD`. `urgency` is `1–5`. `status` enums are defined in `models/enums.py`.
- Health checks: `GET /health` or `GET /db-test-ms2` (DB connectivity) for monitoring.

## Where to find schemas
- Pydantic models for request/response live in `models/` (e.g., `models/recipient.py`, `models/hospital.py`, `models/need.py`).
- Enumerations for blood/organ/status values: `models/enums.py`.
- Full OpenAPI JSON: `GET /openapi.json` (or use `/docs`).
