from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from .enums import OrganType, BloodType, NeedStatus

class NeedBase(BaseModel):
    organ_type: OrganType
    urgency: int = Field(ge=1, le=5, json_schema_extra={"example": 4})
    blood_type: BloodType
    status: NeedStatus = NeedStatus.WAITING

class NeedRead(NeedBase):
    id: UUID = Field(default_factory=uuid4)
    recipient_id: UUID
    listed_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NeedCreate(NeedBase):
    pass

class NeedUpdate(BaseModel):
    organ_type: Optional[OrganType] = None
    urgency: Optional[int] = Field(default=None, ge=1, le=5)
    blood_type: Optional[BloodType] = None
    status: Optional[NeedStatus] = None