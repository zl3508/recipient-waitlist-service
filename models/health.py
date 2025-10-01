from __future__ import annotations
from pydantic import BaseModel, Field

class Health(BaseModel):
    status: int = Field(200, description="Numeric status code (e.g., 200)")
    status_message: str = Field("OK", description="Human-readable status message")
    timestamp: str = Field(description="UTC ISO 8601 timestamp")
    ip_address: str = Field(description="Service IP address")
    echo: str | None = Field(default=None, description="Optional echo (query param)")
    path_echo: str | None = Field(default=None, description="Echo from path param")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": 200,
                "status_message": "OK",
                "timestamp": "2025-09-30T21:05:00Z",
                "ip_address": "127.0.0.1",
                "echo": "hello",
                "path_echo": "world",
            }
        }
    }