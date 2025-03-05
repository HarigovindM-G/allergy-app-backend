from fastapi import APIRouter
from app.api.endpoints import allergens,ocr

router = APIRouter()

router.include_router(
    allergens.router,
    prefix="/allergens",
    tags=["allergens"]
) 

router.include_router(
    ocr.router, prefix="", tags=["OCR"]
) 