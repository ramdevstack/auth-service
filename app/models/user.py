from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    # ----------------------------------------
    # 1. TABLE NAME
    # ----------------------------------------
    # This tells SQLAlchemy what to name the table in the database.
    # Convention: lowercase, plural of the class name.
    __tablename__ = "users"

    # ----------------------------------------
    # 2. COLUMNS
    # ----------------------------------------

    # Primary key — every table needs one.
    # index=True makes lookups by id faster.
    id = Column(Integer, primary_key=True, index=True)

    # Email — must be unique (no two users share an email).
    # index=True because we'll search by email often (login).
    email = Column(String, unique=True, index=True, nullable=False)

    # We NEVER store plain passwords — always store the hash.
    # nullable=False means this column is required.
    hashed_password = Column(String, nullable=False)

    # Lets us deactivate users without deleting their data.
    # default=True means new users are active by default.
    is_active = Column(Boolean, default=True)

    # Automatically sets to current time when a user is created.
    # server_default=func.now() lets the DATABASE set the time
    # (more reliable than Python's datetime.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # ----------------------------------------
    # 3. HELPER METHOD
    # ----------------------------------------
    # Makes it easy to print a User object for debugging.
    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"