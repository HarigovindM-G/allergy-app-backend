from fastapi import APIRouter
from app.api.endpoints import allergens

router = APIRouter()

router.include_router(
    allergens.router,
    prefix="/allergens",
    tags=["allergens"]
) 