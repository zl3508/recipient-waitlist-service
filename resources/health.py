from __future__ import annotations
from fastapi import APIRouter, Query, Path
from models import Health
from utils.ip import get_ip
from utils.time import utcnow_iso_z

router = APIRouter(prefix="/health", tags=["health"])

def make_health(echo: str | None, path_echo: str | None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=utcnow_iso_z(),
        ip_address=get_ip(),
        echo=echo,
        path_echo=path_echo,
    )

@router.get("", response_model=Health)
def health(echo: str | None = Query(default=None)):
    return make_health(echo, None)

@router.get("/{path_echo}", response_model=Health)
def health_with_path(path_echo: str = Path(...), echo: str | None = Query(default=None)):
    return make_health(echo, path_echo)