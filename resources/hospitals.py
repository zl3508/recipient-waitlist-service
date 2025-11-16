from __future__ import annotations
from uuid import UUID

from fastapi import APIRouter, status, Query, Path, HTTPException

from models import HospitalCreate, HospitalRead, HospitalUpdate
from models.enums import CommonStatus
from services.hospitals_service import (
    list_hospitals as svc_list_hospitals,
    create_hospital as svc_create_hospital,
    get_hospital as svc_get_hospital,
    update_hospital as svc_update_hospital,
    delete_hospital as svc_delete_hospital,
)

router = APIRouter(prefix="/hospitals", tags=["hospitals"])


@router.get("", response_model=list[HospitalRead])
def list_hospitals(
    city: str | None = Query(default=None),
    state: str | None = Query(default=None),
    status_q: CommonStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
):
    return svc_list_hospitals(
        city=city,
        state=state,
        status_q=status_q,
        limit=limit,
    )


@router.post("", response_model=HospitalRead, status_code=status.HTTP_201_CREATED)
def create_hospital(h: HospitalCreate):
    return svc_create_hospital(h)


@router.get("/{hospital_id}", response_model=HospitalRead)
def get_hospital(hospital_id: UUID = Path(...)):
    hospital = svc_get_hospital(hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@router.put("/{hospital_id}", response_model=HospitalRead)
def update_hospital(hospital_id: UUID, patch: HospitalUpdate):
    hospital = svc_update_hospital(hospital_id, patch)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@router.delete("/{hospital_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hospital(hospital_id: UUID):
    ok = svc_delete_hospital(hospital_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return
