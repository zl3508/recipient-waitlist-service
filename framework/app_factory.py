from __future__ import annotations

from fastapi import FastAPI

def create_app() -> FastAPI:
    return FastAPI(
        title="Recipient Waitlist Service",
        description="Microservice 2 (Sprint 1) — recipients, hospitals, needs. All endpoints stubbed.",
        version="0.1.0",
    )