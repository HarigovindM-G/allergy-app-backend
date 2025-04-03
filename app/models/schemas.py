from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class TextInput(BaseModel):
    text: str

class AllergenPrediction(BaseModel):
    allergen: str
    confidence: float
    evidence: list[str] | None
    is_user_allergen: Optional[bool] = None

class AllergenResponse(BaseModel):
    allergens: list[AllergenPrediction]
    input_text: str
    threshold_used: float

# Allergy schemas
class AllergyItem(BaseModel):
    id: str  # e.g., "milk"
    name: str  # e.g., "Milk"
    category: str  # e.g., "Dairy"
    severity: Optional[str] = None  # e.g., "High", "Medium", "Low"
    notes: Optional[str] = None

class UserAllergiesUpdate(BaseModel):
    allergies: List[AllergyItem]

# Scan history schemas
class ScanHistoryCreate(BaseModel):
    user_id: Optional[int] = None
    product_name: Optional[str] = None
    input_text: str
    allergens: list[AllergenPrediction]
    image_url: Optional[str] = None

class ScanHistoryResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    product_name: Optional[str] = None
    input_text: str
    allergens: list[AllergenPrediction]
    image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str
    allergies: Optional[List[AllergyItem]] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    allergies: Optional[List[AllergyItem]] = None
    
    class Config:
        from_attributes = True
        
    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        # Ensure allergies is always an array
        if data.get('allergies') is None:
            data['allergies'] = []
        return data

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[datetime] = None
    type: Optional[str] = None

class RefreshToken(BaseModel):
    refresh_token: str

# Medicine schemas
class MedicineBase(BaseModel):
    name: str
    dosage: str
    expiration_date: Optional[str] = None
    notes: Optional[str] = None
    reminder_enabled: Optional[bool] = False
    reminder_time: Optional[str] = None

class MedicineCreate(MedicineBase):
    pass

class MedicineUpdate(MedicineBase):
    pass

class MedicineResponse(MedicineBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 