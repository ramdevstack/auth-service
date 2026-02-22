from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ----------------------------------------
# 1. WHERE is the database?
# ----------------------------------------
# This is the path to your SQLite file.
# SQLite stores the entire database in a single file — auth.db
# It will be created automatically the first time you run the app.
# The "///" means relative path (relative to where you run the app from)
SQLALCHEMY_DATABASE_URL = "sqlite:///./auth.db"

# ----------------------------------------
# 2. HOW do we connect?
# ----------------------------------------
# The engine is the actual connection to the database.
# connect_args={"check_same_thread": False} is SQLite-specific —
# it allows multiple parts of your app to use the same connection.
# (PostgreSQL won't need this later when we upgrade)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ----------------------------------------
# 3. HOW do we talk to it?
# ----------------------------------------
# SessionLocal is a factory — calling SessionLocal() creates a new session.
# autocommit=False → we manually control when changes are saved
# autoflush=False  → we manually control when data is sent to the DB
# bind=engine      → connect this session factory to our engine
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ----------------------------------------
# 4. THE BLUEPRINT
# ----------------------------------------
# All our table classes (User, etc.) will inherit from Base.
# This is how SQLAlchemy knows they represent database tables.
Base = declarative_base()

# ----------------------------------------
# 5. THE SESSION HELPER (Dependency)
# ----------------------------------------
# This function is used by FastAPI to give each request its own
# session, then clean it up automatically when the request is done.
# "yield" makes it a generator — code after yield runs on cleanup.
# This pattern is called a "dependency" in FastAPI.
def get_db():
    db = SessionLocal()   # open a session
    try:
        yield db          # give it to the request handler
    finally:
        db.close()        # always close it, even if an error occurs