from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM
)
from app.models.user import User
from app.models.schemas import UserCreate, UserResponse, Token, RefreshToken
from app.api.deps import get_current_active_user, get_token_from_header

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    """
    # Check if user with this email already exists
    user_by_email = db.query(User).filter(User.email == user_in.email).first()
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if user with this username already exists
    user_by_username = db.query(User).filter(User.username == user_in.username).first()
    if user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    # Try to find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # If not found, try by email
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()
    
    # If still not found or password doesn't match, raise error
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access and refresh tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
def refresh_token(refresh_token_in: RefreshToken, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token_in.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if it's a refresh token
        if payload.get("type") != "refresh":
            raise credentials_exception
        
        # Get the user ID from the token
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    # Get the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    
    # Create new access and refresh tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user.
    """
    return current_user

@router.get("/debug-auth")
async def debug_auth(request: Request, authorization: Optional[str] = Header(None)):
    """
    Debug endpoint to check authentication headers.
    """
    headers = {key: value for key, value in request.headers.items()}
    
    # Try to extract token
    token = None
    if authorization:
        scheme, _, token_value = authorization.partition(" ")
        if scheme.lower() == "bearer":
            token = token_value
    
    # Try to decode token if present
    decoded_token = None
    if token:
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except Exception as e:
            decoded_token = {"error": str(e)}
    
    return {
        "headers": headers,
        "token": token,
        "decoded_token": decoded_token
    }

@router.get("/test")
async def test_endpoint():
    """
    Test endpoint that doesn't require authentication.
    """
    return {"message": "Test endpoint is working!"} 