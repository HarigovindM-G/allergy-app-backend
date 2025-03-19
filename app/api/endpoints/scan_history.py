from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.models.schemas import ScanHistoryCreate, ScanHistoryResponse
from app.models.scan_history import ScanHistory
from app.api.deps import get_current_user_optional

router = APIRouter()

@router.post("/", response_model=ScanHistoryResponse)
def create_scan_history(
    scan_data: ScanHistoryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Create a new scan history entry."""
    # Print the incoming data for debugging
    print(f"Received scan data: {scan_data}")
    
    # User is optional, if logged in we'll associate the scan
    user_id = current_user.id if current_user else None
    
    # If user is logged in and no user_id provided, use the current user
    if user_id and not scan_data.user_id:
        scan_data.user_id = user_id
    
    # Process allergens properly for storage
    try:
        # Create DB record with minimal processing
        db_scan = ScanHistory(
            user_id=scan_data.user_id,
            product_name=scan_data.product_name,
            input_text=scan_data.input_text,
            allergens=scan_data.allergens,
            image_url=scan_data.image_url
        )
        
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        
        print(f"Created scan history with ID: {db_scan.id}")
        
        # Create response
        response = {
            "id": db_scan.id,
            "user_id": db_scan.user_id,
            "product_name": db_scan.product_name,
            "input_text": db_scan.input_text,
            "allergens": db_scan.allergens,
            "image_url": db_scan.image_url,
            "created_at": db_scan.created_at
        }
        
        return response
    except Exception as e:
        import traceback
        print(f"Error creating scan history: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error creating scan history: {str(e)}")

@router.get("/", response_model=List[ScanHistoryResponse])
def get_scan_history(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get scan history for the current user."""
    # If not logged in, return only device-specific entries (no user_id)
    if not current_user:
        query = db.query(ScanHistory).filter(ScanHistory.user_id.is_(None))
    else:
        # If logged in, return the user's entries
        query = db.query(ScanHistory).filter(ScanHistory.user_id == current_user.id)
    
    results = query.order_by(ScanHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert database results to response format
    response_items = []
    for item in results:
        response_item = {
            "id": item.id,
            "user_id": item.user_id,
            "product_name": item.product_name,
            "input_text": item.input_text,
            "allergens": item.allergens,  # This should already be a list of dicts
            "image_url": item.image_url,
            "created_at": item.created_at
        }
        response_items.append(response_item)
    
    return response_items

@router.get("/{scan_id}", response_model=ScanHistoryResponse)
def get_scan_detail(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Get detail for a specific scan history entry."""
    scan = db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan history not found")
    
    # Check permissions - users can only see their own scans or anonymous scans
    if scan.user_id and current_user and scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this scan")
    
    # Convert to response format
    response = {
        "id": scan.id,
        "user_id": scan.user_id,
        "product_name": scan.product_name,
        "input_text": scan.input_text,
        "allergens": scan.allergens,
        "image_url": scan.image_url,
        "created_at": scan.created_at
    }
    
    return response

@router.delete("/{scan_id}")
def delete_scan_history(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_optional)
):
    """Delete a scan history entry."""
    scan = db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan history not found")
    
    # Check permissions - users can only delete their own scans or anonymous scans
    if scan.user_id and current_user and scan.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this scan")
    
    db.delete(scan)
    db.commit()
    
    return {"message": "Scan history deleted successfully"} 