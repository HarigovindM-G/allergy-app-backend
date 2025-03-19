from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import json

class ScanHistory(Base):
    """Scan history database model."""
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_name = Column(String(255), nullable=True)
    input_text = Column(Text, nullable=False)
    allergens = Column(JSON, nullable=False)  # Store allergen data as JSON
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __init__(self, **kwargs):
        # Ensure allergens is properly serialized to JSON
        if 'allergens' in kwargs and kwargs['allergens'] is not None:
            try:
                # If already a string, leave it alone
                if isinstance(kwargs['allergens'], str):
                    pass
                # If a list, ensure it's properly serialized
                elif isinstance(kwargs['allergens'], list):
                    # Convert to JSON string first, then parse back to ensure it's valid JSON
                    kwargs['allergens'] = json.loads(json.dumps(kwargs['allergens']))
                else:
                    # For any other type, try to convert to JSON
                    kwargs['allergens'] = json.loads(json.dumps(kwargs['allergens']))
            except Exception as e:
                print(f"Error serializing allergens: {e}")
                # Default to empty list if we can't serialize
                kwargs['allergens'] = []
                
        super().__init__(**kwargs) 