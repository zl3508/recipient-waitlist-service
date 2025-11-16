from __future__ import annotations
from uuid import UUID

from fastapi import APIRouter, status, Query, Path, HTTPException

from models import RecipientCreate, RecipientRead, RecipientUpdate, NeedCreate, NeedRead
from models.enums import BloodType, CommonStatus
from services.recipients_service import (
    list_recipients as svc_list_recipients,
    create_recipient as svc_create_recipient,
    get_recipient as svc_get_recipient,
    update_recipient as svc_update_recipient,
    delete_recipient as svc_delete_recipient,
)
from utils.responses import not_implemented  # 下面 needs 那部分暂时还是 501


from models.enums import BloodType, CommonStatus, OrganType, NeedStatus
from services.needs_service import (
    list_needs as svc_list_needs,
    create_need as svc_create_need,
)
from services.recipients_service import get_recipient as svc_get_recipient

router = APIRouter(prefix="/recipients", tags=["recipients"])


@router.get("", response_model=list[RecipientRead])
def list_recipients(
    blood_type: BloodType | None = Query(default=None),
    status_q: CommonStatus | None = Query(default=None, alias="status"),
    hospital_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    return svc_list_recipients(
        blood_type=blood_type,
        status_q=status_q,
        hospital_id=hospital_id,
        limit=limit,
    )


@router.post("", response_model=RecipientRead, status_code=status.HTTP_201_CREATED)
def create_recipient(r: RecipientCreate):
    return svc_create_recipient(r)


@router.get("/{recipient_id}", response_model=RecipientRead)
def get_recipient(recipient_id: UUID = Path(...)):
    recipient = svc_get_recipient(recipient_id)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient


@router.put("/{recipient_id}", response_model=RecipientRead)
def update_recipient(recipient_id: UUID, patch: RecipientUpdate):
    recipient = svc_update_recipient(recipient_id, patch)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return recipient


@router.delete("/{recipient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipient(recipient_id: UUID):
    ok = svc_delete_recipient(recipient_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Recipient not found")
    return


# --- /recipients/{id}/needs  ---

@router.get(
    "/{recipient_id}/needs",
    response_model=list[NeedRead],
    tags=["needs"],
)
def list_needs_for_recipient(
    recipient_id: UUID,
    organ_type: OrganType | None = Query(default=None),
    status_q: NeedStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=200),
):
    #confirm recipient exist
    recipient = svc_get_recipient(recipient_id)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")

    return svc_list_needs(
        organ_type=organ_type,
        status_q=status_q,
        recipient_id=recipient_id,
        limit=limit,
    )


@router.post(
    "/{recipient_id}/needs",
    response_model=NeedRead,
    status_code=status.HTTP_201_CREATED,
    tags=["needs"],
)
def create_need_for_recipient(recipient_id: UUID, n: NeedCreate):
    # confirm recipient exist
    recipient = svc_get_recipient(recipient_id)
    if recipient is None:
        raise HTTPException(status_code=404, detail="Recipient not found")

    return svc_create_need(recipient_id=recipient_id, n=n)

