from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.schemas import TokenPayload
from app.models.user import User

# Configure OAuth2 with the correct token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

async def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Extract token from Authorization header.
    """
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            return None
        
        if not token or not isinstance(token, str):
            return None
            
        return token.strip()
    except Exception:
        return None

async def get_current_user(
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None)
) -> User:
    """
    Get the current user from the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = await get_token_from_header(authorization)
    if not token:
        raise credentials_exception
    
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if it's an access token
        if payload.get("type") != "access":
            raise credentials_exception
        
        # Get the user ID from the token
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        # Convert string user_id to integer
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise credentials_exception
        
    except JWTError as e:
        print(f"JWT Error: {str(e)}")  # Add logging
        raise credentials_exception
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Add logging
        raise credentials_exception
    
    # Get the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    Get the current user from the token if it exists and is valid.
    Returns None if no token or token is invalid.
    """
    if not token:
        return None
    
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if it's an access token
        if payload.get("type") != "access":
            return None
        
        # Get the user ID from the token
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
            
        # Convert string user_id to integer
        try:
            user_id = int(user_id_str)
        except ValueError:
            return None
        
    except JWTError:
        return None
    
    # Get the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user 