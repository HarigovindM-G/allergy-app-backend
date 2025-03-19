from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

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

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

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