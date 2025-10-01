from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Recipient Waitlist API — see /docs"}