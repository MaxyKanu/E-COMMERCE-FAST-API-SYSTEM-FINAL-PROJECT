"""
Authentication Router
Handles user registration, login, and profile retrieval
Uses REAL JWT token generation with database verification
Includes .strip() to clean accidental spaces in email input
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, Token
from app.crud.user import get_user_by_email, create_user
from app.utils.hashing import authenticate_user
from app.utils.auth import create_access_token, get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Email must be unique."
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account
    
    - Checks if email already exists
    - Hashes password with bcrypt
    - Returns user data (without password)
    
    Raises:
        400: If email is already registered
    """
    # Strip whitespace from email to prevent accidental spaces
    cleaned_email = user_data.email.strip().lower()
    
    # Check if email already registered
    existing_user = get_user_by_email(db, email=cleaned_email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Update the user data with cleaned email
    user_data.email = cleaned_email
    
    # Create new user with hashed password
    user = create_user(db, user_data)
    
    return user


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Login and get JWT token",
    description="Authenticate with email and password to receive a JWT access token. "
                "Token expires after 30 minutes. Email is automatically cleaned of spaces."
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return a REAL JWT access token
    
    Flow:
    1. Receive email (username field) and password from form
    2. CLEAN the email by stripping whitespace
    3. Look up user in database
    4. Verify password with bcrypt
    5. Generate signed JWT token with user claims
    6. Return token to client
    
    The token includes:
    - user_id: For identifying the user
    - email: User's email address
    - is_admin: Whether user has admin privileges
    
    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session
    
    Returns:
        Token object with access_token and token_type
    
    Raises:
        401: If email or password is incorrect
    """
    # BUG FIX: Strip whitespace from email to prevent " admin@example.com" errors
    # This fixes the hidden space bug where Swagger UI adds leading/trailing spaces
    clean_email = form_data.username.strip().lower()
    clean_password = form_data.password
    
    # Debug logging to verify email is clean
    print(f"🔍 Login attempt for email: '{clean_email}' (spaces removed)")
    
    # Authenticate user against database with CLEAN email
    user = authenticate_user(db, clean_email, clean_password)
    
    if not user:
        print(f"❌ Login failed for: '{clean_email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"✅ Login successful for: {user.email} (Admin: {user.is_admin})")
    
    # Create REAL JWT token with user claims
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "is_admin": user.is_admin
        }
    )
    
    # Return token in expected format
    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user. "
                "Requires a valid JWT token in the Authorization header."
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get the current authenticated user's profile
    
    - Requires valid JWT token in Authorization header
    - Token is automatically extracted and validated by get_current_user dependency
    - Returns user data (without password)
    
    This endpoint is useful for:
    - Verifying your token is working
    - Getting your user ID and role
    - Checking if you're logged in as admin
    
    BUG FIX: Now properly uses Depends(get_current_user) to validate the token
    """
    return current_user