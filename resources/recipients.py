from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, status, Query, Path
from fastapi.responses import JSONResponse
from models import RecipientCreate, RecipientRead, RecipientUpdate, NeedCreate, NeedRead
from utils.responses import not_implemented

router = APIRouter(prefix="/recipients", tags=["recipients"])

@router.get("", response_model=list[RecipientRead])
def list_recipients(
    blood_type: str | None = Query(default=None),
    status_q: str | None = Query(default=None, alias="status"),
    hospital_id: UUID | None = Query(default=None)
):
    return not_implemented()

@router.post("", response_model=RecipientRead, status_code=status.HTTP_201_CREATED)
def create_recipient(r: RecipientCreate):
    return not_implemented()

@router.get("/{recipient_id}", response_model=RecipientRead)
def get_recipient(recipient_id: UUID = Path(...)):
    return not_implemented()

@router.put("/{recipient_id}", response_model=RecipientRead)
def update_recipient(recipient_id: UUID, patch: RecipientUpdate):
    return not_implemented()

@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipient(recipient_id: UUID):
    return not_implemented()

# sub-resource: /recipients/{id}/needs
@router.get("/{recipient_id}/needs", response_model=list[NeedRead], tags=["needs"])
def list_needs_for_recipient(recipient_id: UUID):
    return not_implemented()

@router.post("/{recipient_id}/needs", response_model=NeedRead, status_code=status.HTTP_201_CREATED, tags=["needs"])
def create_need_for_recipient(recipient_id: UUID, n: NeedCreate):
    return not_implemented()