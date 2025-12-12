from fastapi import APIRouter, status, Path, HTTPException, Query
from uuid import UUID

from models import NeedRead, NeedUpdate
from models.enums import OrganType, NeedStatus
from services.needs_service import (
    list_needs as svc_list_needs,
    get_need as svc_get_need,
    update_need as svc_update_need,
    delete_need as svc_delete_need,
)

from services.recipients_service import get_recipient as svc_get_recipient  

router = APIRouter(prefix="/needs", tags=["needs"])

@router.get("", response_model=list[NeedRead])
def list_needs(
    organ_type: OrganType | None = Query(default=None),
    status_q: NeedStatus | None = Query(default=None, alias="status"),
    recipient_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    if recipient_id is not None:
        recipient = svc_get_recipient(recipient_id)
        if recipient is None:
            raise HTTPException(status_code=404, detail="Recipient not found")

    return svc_list_needs(
        organ_type=organ_type,
        status_q=status_q,
        recipient_id=recipient_id,
        limit=limit,
    )

@router.get("/{need_id}", response_model=NeedRead)
def get_need(need_id: UUID = Path(...)):
    need = svc_get_need(need_id)
    if need is None:
        raise HTTPException(status_code=404, detail="Need not found")
    return need


@router.put("/{need_id}", response_model=NeedRead)
def update_need(need_id: UUID, patch: NeedUpdate):
    need = svc_update_need(need_id, patch)
    if need is None:
        raise HTTPException(status_code=404, detail="Need not found")
    return need


@router.delete("/{need_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_need(need_id: UUID):
    ok = svc_delete_need(need_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Need not found")
    return
