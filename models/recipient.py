from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from .enums import BloodType, CommonStatus

class RecipientBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200, json_schema_extra={"example": "Jane Doe"})
    dob: date = Field(..., json_schema_extra={"example": "1990-05-20"})
    blood_type: BloodType
    status: CommonStatus = CommonStatus.ACTIVE
    primary_hospital_id: Optional[UUID] = Field(default=None)

class RecipientRead(RecipientBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class RecipientCreate(RecipientBase):
    pass

class RecipientUpdate(BaseModel):
    full_name: Optional[str] = None
    dob: Optional[date] = None
    blood_type: Optional[BloodType] = None
    status: Optional[CommonStatus] = None
    primary_hospital_id: Optional[UUID] = None