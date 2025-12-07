# Recipient Waitlist Service (MS2) – Checklist Coverage

This document highlights which final project checklist items are satisfied by the **MS2 Recipient Waitlist microservice** contained in this repository. Items marked ✅ are covered by this codebase; items marked ❌ remain outside this service or are not implemented here.

## Completed in MS2 (✅)
- ✅ **Atomic microservice implementation**: This repository delivers one of the required atomic services (Recipient Waitlist) with FastAPI routing and Pydantic models that generate OpenAPI docs automatically via the FastAPI app factory in `main.py`.
- ✅ **CRUD for all resources**: Recipients, hospitals, and needs each expose GET, POST, PUT, and DELETE, plus nested subresources such as `/recipients/{recipient_id}/needs` and `/recipients/{recipient_id}/hospital`. All POST routes return HTTP 201 and DELETE returns 204.
- ✅ **Query parameters on collections**: Collection endpoints accept filters (e.g., status, blood type, organ type, city/state/phone) to narrow results across `/recipients`, `/hospitals`, and `/needs`.
- ✅ **Basic pagination/bounding**: Collection routes accept a `limit` parameter to bound the number of results, providing minimal pagination support.
- ✅ **Linked data via relative paths**: Nested routes (e.g., `/recipients/{recipient_id}/needs`, `/recipients/{recipient_id}/hospital`) validate the parent resource and traverse relationships through relative paths.
- ✅ **Database-backed persistence**: Services layer reads/writes MySQL (configured for Cloud SQL or VM), including a `/db-test-ms2` connectivity endpoint.
- ✅ **Deployment-ready**: Dockerfile and README document Cloud Run deployment for this microservice, covering the requirement for at least one microservice deployed on Cloud Run.

## Not Implemented in MS2 (❌)
- ❌ **eTag processing** for conditional requests.
- ❌ **202 Accepted with async/polling** workflows.
- ❌ **OAuth2/OIDC + JWT enforcement** on endpoints.
- ❌ **Google Cloud Function trigger** and event emission.
- ❌ **Composite microservice logic** (aggregation/parallel calls) and **Swagger API-first microservice** (MS3) — these belong to other repositories.
- ❌ **Browser UI deployment** and the remaining repositories required to reach six total are out of scope for this single-service repo.
