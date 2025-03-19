from fastapi import APIRouter, Depends
from typing import List, Optional
from app.models.schemas import TextInput
from app.services.allergen_detector import AllergenDetector
from app.api.deps import get_current_user_optional
from app.models.user import User

router = APIRouter()
detector = AllergenDetector()

@router.post("/detect")
def detect_allergens(
    input_data: TextInput,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Detect allergens in text and mark user's known allergies"""
    result = detector.detect(input_data.text)
    
    # If user is logged in and has allergies, mark matching allergens
    if current_user and hasattr(current_user, 'allergies') and current_user.allergies:
        user_allergies = current_user.allergies
        user_allergy_ids = [allergy.get("id", "").lower() for allergy in user_allergies if isinstance(allergy, dict) and "id" in allergy]
        
        # Mark allergens that match user's known allergies
        for allergen in result["allergens"]:
            allergen_normalized = allergen["allergen"].lower().replace(" ", "_")
            if allergen_normalized in user_allergy_ids or any(aid in allergen_normalized for aid in user_allergy_ids):
                allergen["is_user_allergen"] = True
            else:
                allergen["is_user_allergen"] = False
    else:
        # If no user or no allergies, mark all as not user allergens
        for allergen in result["allergens"]:
            allergen["is_user_allergen"] = False
    
    return result 