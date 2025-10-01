from fastapi import status
from fastapi.responses import JSONResponse

def not_implemented():
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"detail": "NOT_IMPLEMENTED (Sprint 1 stub)"}
    )