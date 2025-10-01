from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from .enums import CommonStatus

class HospitalBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, json_schema_extra={"example": "NY Presbyterian"})
    city: Optional[str] = Field(default=None, json_schema_extra={"example": "New York"})
    state: Optional[str] = Field(default=None, json_schema_extra={"example": "NY"})
    phone: Optional[str] = Field(default=None, json_schema_extra={"example": "+1-212-555-0101"})
    status: CommonStatus = CommonStatus.ACTIVE

class HospitalRead(HospitalBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HospitalCreate(HospitalBase):
    pass

class HospitalUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    city: Optional[str] = None
    state: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[CommonStatus] = None