from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth
from app.core.config import settings

# ----------------------------------------
# 1. CREATE DATABASE TABLES
# ----------------------------------------
# This reads all classes that inherit from Base (like our User model)
# and creates the corresponding tables in SQLite if they don't exist.
# Safe to run multiple times — won't overwrite existing tables.
Base.metadata.create_all(bind=engine)

# ----------------------------------------
# 2. CREATE FASTAPI APP
# ----------------------------------------
app = FastAPI(
    title=settings.app_name,
    description="Authentication & Authorization Service",
    version="1.0.0",
    # Enables the interactive docs at /docs
    docs_url="/docs",
    # Enables alternative docs at /redoc
    redoc_url="/redoc"
)

# ----------------------------------------
# 3. ADD CORS MIDDLEWARE
# ----------------------------------------
# Allows browsers to call this API from different origins.
# In development we allow everything ("*").
# In production you'd replace "*" with your actual frontend URL
# e.g. ["https://myapp.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # which domains can call us
    allow_credentials=True,    # allow cookies/auth headers
    allow_methods=["*"],       # allow all HTTP methods
    allow_headers=["*"],       # allow all headers
)

# ----------------------------------------
# 4. REGISTER ROUTERS
# ----------------------------------------
# This plugs in all the routes from auth.py
# All routes get the /auth prefix (defined in the router itself)
app.include_router(auth.router)

# ----------------------------------------
# 5. ROOT ENDPOINT
# ----------------------------------------
# A simple health check — useful to verify the server is running
@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "status": "running"
    }

# ----------------------------------------
# 6. HEALTH CHECK ENDPOINT
# ----------------------------------------
# Standard practice — monitoring tools ping this to check
# if your service is alive
@app.get("/health")
def health_check():
    return {"status": "healthy"}