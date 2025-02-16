from fastapi import APIRouter
from app.models.schemas import TextInput
from app.services.allergen_detector import AllergenDetector

router = APIRouter()
detector = AllergenDetector()

@router.post("/detect")
def detect_allergens(input_data: TextInput):
    return detector.detect(input_data.text) 