from fastapi import APIRouter
from app.api.endpoints import allergens, ocr, auth, test

router = APIRouter()

router.include_router(
    allergens.router,
    prefix="/allergens",
    tags=["allergens"]
) 

router.include_router(
    ocr.router, prefix="", tags=["OCR"]
) 

router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

router.include_router(
    test.router,
    prefix="/test",
    tags=["test"]
) 