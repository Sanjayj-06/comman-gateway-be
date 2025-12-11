from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.routers import users, rules, commands, audit, approvals

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Command Gateway API",
    description="A command execution gateway with rule-based access control and credit system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(rules.router)
app.include_router(commands.router)
app.include_router(audit.router)
app.include_router(approvals.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Command Gateway API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/debug/check-admin")
async def check_admin():
    """Debug endpoint to check admin user (REMOVE IN PRODUCTION)"""
    from app.db.session import get_db
    from app.db.models import User
    
    db = next(get_db())
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            return {
                "admin_exists": True,
                "username": admin.username,
                "api_key": admin.api_key,
                "role": admin.role,
                "credits": admin.credits
            }
        else:
            return {"admin_exists": False}
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
