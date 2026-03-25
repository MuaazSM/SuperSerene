"""Authentication API routes.

Endpoints:
- POST /auth/login - User login
- POST /auth/signup - User registration
"""

from fastapi import APIRouter, HTTPException, status, Depends, Request
from datetime import datetime, timezone
from pydantic import BaseModel
from passlib.context import CryptContext

from logger.custom_logger import CustomLogger
from api.deps import get_db, get_orchestrator
from services.auth_service import AuthService
from auth import login_redirect, google_callback

_LOG = CustomLogger().get_logger(__name__)

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Request/Response models
class LoginRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user_id: str
    email: str
    name: str


def get_auth_service(
    db=Depends(get_db),
    orchestrator=Depends(get_orchestrator),
) -> AuthService:
    """Dependency provider for AuthService."""
    return AuthService(db=db, orchestrator=orchestrator)


@router.get("/google/login", tags=["authentication"])
async def google_login(request: Request):
    """Start Google OAuth login by redirecting to provider."""
    return await login_redirect(request)


@router.get("/google/callback", tags=["authentication"])
async def google_oauth_callback(request: Request):
    """Handle Google OAuth callback and redirect to frontend with JWT."""
    return await google_callback(request)


@router.post("/login", response_model=AuthResponse, tags=["authentication"])
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Login with email and password.
    
    Args:
        request: Login credentials (email, password)
        
    Returns:
        AuthResponse with JWT token and user info
        
    Raises:
        HTTPException: 401 if credentials invalid, 500 on error
    """
    try:
        result = await service.login(request.email, request.password)
        return AuthResponse(**result)

    except ValueError as e:
        _LOG.warning("Login validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except Exception as e:
        _LOG.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("/signup", response_model=AuthResponse, tags=["authentication"])
async def signup(
    request: SignupRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Signup with email and password.
    
    Args:
        request: Signup info (email, password, name)
        
    Returns:
        AuthResponse with JWT token and user info
        
    Raises:
        HTTPException: 400 if validation fails, 409 if email exists, 500 on error
    """
    try:
        result = await service.signup(
            name=request.name,
            email=request.email,
            password=request.password,
        )
        return AuthResponse(**result)

    except ValueError as e:
        code = status.HTTP_400_BAD_REQUEST if "password" in str(e).lower() or "required" in str(e).lower() else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(e))
    except Exception as e:
        _LOG.error("Signup failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed. Please try again."
        )
