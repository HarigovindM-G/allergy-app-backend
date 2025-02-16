from pydantic import BaseModel

class TextInput(BaseModel):
    text: str

class AllergenPrediction(BaseModel):
    allergen: str
    confidence: float
    evidence: list[str] | None

class AllergenResponse(BaseModel):
    allergens: list[AllergenPrediction]
    input_text: str
    threshold_used: float 