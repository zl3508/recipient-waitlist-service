from fastapi import APIRouter
from .health import router as health
from .hospitals import router as hospitals
from .recipients import router as recipients
from .needs import router as needs
from .root import router as root

api = APIRouter()
api.include_router(root)
api.include_router(health)
api.include_router(hospitals)
api.include_router(recipients)
api.include_router(needs)