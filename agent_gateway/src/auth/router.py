"""
Authentication FastAPI Router & Endpoint Definitions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any

from .auth_service import verify_user_credentials, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

#pydantic schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    customer_type: str

#Authentication dependency for protected routes
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user = verify_user_credentials(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    token = create_access_token(
        user_id=user["user_id"],
        username=user["username"],
        customer_type=user["customer_type"]
    )

    return TokenResponse(
        access_token=token,
        user_id=user["user_id"],
        username=user["username"],
        customer_type=user["customer_type"]
    )


@router.get("/me")
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the authenticated user details from the JWT Bearer token."""
    return {
        "authenticated": True,
        "user": current_user
    }
