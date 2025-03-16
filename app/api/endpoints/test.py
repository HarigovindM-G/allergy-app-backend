from fastapi import APIRouter, Depends, Header, Request
from typing import Optional
from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM

router = APIRouter()

@router.get("/")
async def test_endpoint():
    """
    Test endpoint that doesn't require authentication.
    """
    return {"message": "Test endpoint is working!"}

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