from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.endpoints import auth, users, resources
from .api.middleware.authorization import AuthorizationMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
)

# Set up CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authorization middleware
# You can uncomment this to enable global authorization checks
# app.add_middleware(AuthorizationMiddleware)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["users"])
app.include_router(resources.router, prefix=f"{settings.API_PREFIX}/resources", tags=["resources"])

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI with Casbin RBAC"}

# Add a startup event to load some sample users if the users_db is empty
@app.on_event("startup")
def startup_event():
    from .models.user import users_db, User
    from .core.security import get_password_hash
    from .core.casbin_rbac import CasbinEnforcer
    import uuid
    
    # Add sample users if the users_db is empty
    if not users_db:
        # Admin user
        admin_id = str(uuid.uuid4())
        admin = User(
            id=admin_id,
            email="admin@example.com",
            username="admin_user",
            hashed_password=get_password_hash("adminpassword"),
            full_name="Admin User",
            role="admin",
        )
        users_db[admin_id] = admin
        
        # Manager user
        manager_id = str(uuid.uuid4())
        manager = User(
            id=manager_id,
            email="manager@example.com",
            username="manager_user",
            hashed_password=get_password_hash("managerpassword"),
            full_name="Manager User",
            role="manager",
        )
        users_db[manager_id] = manager
        
        # Regular user
        user_id = str(uuid.uuid4())
        regular_user = User(
            id=user_id,
            email="user@example.com",
            username="regular_user",
            hashed_password=get_password_hash("userpassword"),
            full_name="Regular User",
            role="user",
        )
        users_db[user_id] = regular_user