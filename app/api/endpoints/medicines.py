from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.schemas import MedicineCreate, MedicineUpdate, MedicineResponse
from app.models.medicine import Medicine
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[MedicineResponse])
def get_medicines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all medicines for the current user."""
    try:
        medicines = db.query(Medicine).filter(Medicine.user_id == current_user.id).all()
        return medicines
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new medicine entry."""
    try:
        db_medicine = Medicine(
            **medicine.model_dump(),
            user_id=current_user.id
        )
        db.add(db_medicine)
        db.commit()
        db.refresh(db_medicine)
        return db_medicine
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{medicine_id}", response_model=MedicineResponse)
def update_medicine(
    medicine_id: int,
    medicine: MedicineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a medicine entry."""
    try:
        db_medicine = db.query(Medicine).filter(
            Medicine.id == medicine_id,
            Medicine.user_id == current_user.id
        ).first()
        
        if not db_medicine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medicine not found"
            )
        
        update_data = medicine.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_medicine, key, value)
        
        db_medicine.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_medicine)
        return db_medicine
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a medicine entry."""
    try:
        db_medicine = db.query(Medicine).filter(
            Medicine.id == medicine_id,
            Medicine.user_id == current_user.id
        ).first()
        
        if not db_medicine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medicine not found"
            )
        
        db.delete(db_medicine)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 