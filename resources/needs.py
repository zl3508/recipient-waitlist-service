from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, status, Path
from models import NeedRead, NeedUpdate
from utils.responses import not_implemented

router = APIRouter(prefix="/needs", tags=["needs"])

@router.get("/{need_id}", response_model=NeedRead)
def get_need(need_id: UUID = Path(...)):
    return not_implemented()

@router.put("/{need_id}", response_model=NeedRead)
def update_need(need_id: UUID, patch: NeedUpdate):
    return not_implemented()

@router.delete("/{need_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_need(need_id: UUID):
    return not_implemented()