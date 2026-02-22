from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ----------------------------------------
# 1. USER CREATION (Registration)
# ----------------------------------------
# This is what the client sends when registering.
# We expect exactly these two fields — nothing more, nothing less.
# Pydantic automatically validates that email looks like an email
# and that password is a string.
class UserCreate(BaseModel):
    email: EmailStr        # validates it's a real email format
    password: str          # plain password (we'll hash it before storing)

# ----------------------------------------
# 2. USER LOGIN
# ----------------------------------------
# What the client sends when logging in.
# Identical to UserCreate here, but kept separate intentionally —
# login and register might diverge later (e.g. login adds "remember me")
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ----------------------------------------
# 3. USER RESPONSE
# ----------------------------------------
# What we send BACK to the client.
# Notice: no password field — we never expose that.
# Optional[datetime] means created_at might be None in edge cases.
class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: Optional[datetime] = None

    # This tells Pydantic: "you can build this schema from a
    # SQLAlchemy model object, not just a plain dictionary."
    # Without this, UserResponse(user) would fail.
    class Config:
        from_attributes = True

# ----------------------------------------
# 4. TOKEN RESPONSE
# ----------------------------------------
# What we send back after a successful login.
# access_token → the JWT string the client stores and sends with requests
# token_type   → always "bearer" (industry standard)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"   # default value — always "bearer"

# ----------------------------------------
# 5. TOKEN DATA (Internal Use)
# ----------------------------------------
# Used internally when we decode a JWT to extract who it belongs to.
# Optional because a token might be invalid/expired.
class TokenData(BaseModel):
    email: Optional[str] = None