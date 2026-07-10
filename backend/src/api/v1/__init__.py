from fastapi import APIRouter
from src.api.v1 import alert
from src.api.v1 import file


router = APIRouter(prefix="/v1")
router.include_router(alert.router)
router.include_router(file.router)
