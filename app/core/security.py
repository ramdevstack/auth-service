from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# ----------------------------------------
# 1. PASSWORD HASHING SETUP
# ----------------------------------------
# CryptContext manages password hashing schemes.
# schemes=["bcrypt"] → use bcrypt algorithm (industry standard)
# deprecated="auto"  → automatically upgrade old hashes if we
#                       ever switch algorithms in the future
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------------------------------
# 2. PASSWORD FUNCTIONS
# ----------------------------------------

def hash_password(plain_password: str) -> str:
    """
    Takes a plain text password and returns a bcrypt hash.
    Called during registration before saving to database.

    Example:
        hash_password("mypassword123")
        → "$2b$12$Kx8Qv7Z..."
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain password matches a stored hash.
    Called during login to verify the user's password.

    Returns True if match, False if not.

    Example:
        verify_password("mypassword123", "$2b$12$Kx8Qv7Z...")
        → True

        verify_password("wrongpassword", "$2b$12$Kx8Qv7Z...")
        → False
    """
    return pwd_context.verify(plain_password, hashed_password)


# ----------------------------------------
# 3. JWT TOKEN FUNCTIONS
# ----------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT token containing the given data.
    Called after successful login.

    data          → dict of what to store in the token (e.g. {"email": "user@example.com"})
    expires_delta → how long until token expires (defaults to settings value)

    Returns the JWT token as a string.
    """
    # Copy the data so we don't modify the original dict
    to_encode = data.copy()

    # Set expiry time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    # Add expiry to the token payload
    # "exp" is a standard JWT claim — jose automatically
    # checks this when we decode the token later
    to_encode.update({"exp": expire})

    # Sign and encode the token using our secret key
    # This produces the final JWT string
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[str]:
    """
    Decodes a JWT token and returns the email inside it.
    Called on protected routes to identify who is making the request.

    Returns the email string if valid, None if invalid/expired.
    """
    try:
        # Decode and verify the token
        # jose automatically checks:
        #   - signature is valid (nobody tampered with it)
        #   - token hasn't expired
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        # Extract email from payload
        # "sub" is JWT standard for "subject" (who this token is about)
        email: str = payload.get("sub")

        if email is None:
            return None

        return email

    except JWTError:
        # Token is invalid, expired, or tampered with
        return None