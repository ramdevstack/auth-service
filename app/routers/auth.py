from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

# ----------------------------------------
# 1. ROUTER SETUP
# ----------------------------------------
# prefix="/auth" means all routes here start with /auth
# e.g. register becomes /auth/register
# tags=["auth"] groups these endpoints in the API docs
router = APIRouter(prefix="/auth", tags=["auth"])

# ----------------------------------------
# 2. OAuth2 SCHEME
# ----------------------------------------
# Tells FastAPI: "tokens come from /auth/login"
# Used to extract the token from the Authorization header
# on protected routes like /auth/me
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ----------------------------------------
# 3. HELPER: GET CURRENT USER
# ----------------------------------------
# This is a dependency — FastAPI calls it automatically
# on any route that needs authentication.
# It extracts the token, decodes it, finds the user in DB.
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # If token is invalid return 401 Unauthorized
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the token to get email
    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    # Find the user in the database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


# ----------------------------------------
# 4. REGISTER ENDPOINT
# ----------------------------------------
# response_model=UserResponse → automatically shapes
# the response using our schema (hides password, etc.)
# status_code=201 → HTTP 201 Created (more correct than 200 for creation)
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    - Checks email isn't already taken
    - Hashes the password
    - Saves user to database
    - Returns the new user (without password)
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash the password before storing
    hashed = hash_password(user_data.password)

    # Create new User model instance
    new_user = User(
        email=user_data.email,
        hashed_password=hashed
    )

    # Save to database
    # add()    → stage the new user
    # commit() → save to disk
    # refresh()→ reload from DB (gets the auto-generated id, created_at)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ----------------------------------------
# 5. LOGIN ENDPOINT
# ----------------------------------------
@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.

    - Finds user by email
    - Verifies password against stored hash
    - Returns a JWT access token
    """
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()

    # Deliberately vague error — don't tell attacker
    # whether email or password was wrong
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is disabled"
        )

    # Create JWT token with user's email as the subject
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


# ----------------------------------------
# 6. ME ENDPOINT (Protected)
# ----------------------------------------
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the currently logged in user's info.

    - Requires a valid JWT token in Authorization header
    - Returns user data (without password)
    """
    # get_current_user dependency already did all the work
    # current_user is the User object from the database
    return current_user