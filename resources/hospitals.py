from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, status, Query, Path
from fastapi.responses import JSONResponse
from models import HospitalCreate, HospitalRead, HospitalUpdate
from utils.responses import not_implemented

router = APIRouter(prefix="/hospitals", tags=["hospitals"])

@router.get("", response_model=list[HospitalRead])
def list_hospitals(
    city: str | None = Query(default=None),
    state: str | None = Query(default=None),
    status_q: str | None = Query(default=None, alias="status")
):
    return not_implemented()

@router.post("", response_model=HospitalRead, status_code=status.HTTP_201_CREATED)
def create_hospital(h: HospitalCreate):
    return not_implemented()

@router.get("/{hospital_id}", response_model=HospitalRead)
def get_hospital(hospital_id: UUID = Path(...)):
    return not_implemented()

@router.put("/{hospital_id}", response_model=HospitalRead)
def update_hospital(hospital_id: UUID, patch: HospitalUpdate):
    return not_implemented()

@router.delete("/{hospital_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hospital(hospital_id: UUID):
    return not_implemented()