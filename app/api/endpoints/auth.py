from datetime import timedelta
from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ...core.security import create_access_token, get_password_hash, verify_password
from ...config import settings
from ...models.user import users_db, User
from ...schemas.token import Token
from ...schemas.user import UserCreate
from ...core.casbin_rbac import CasbinEnforcer

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Get an access token for future requests using OAuth2 password flow
    """
    user = None
    for u in users_db.values():
        if u.username == form_data.username:
            user = u
            break
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.id, role=user.role, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=Token)
def register_user(user_in: UserCreate) -> Any:
    """
    Register a new user
    """
    # Check if the user already exists
    for existing_user in users_db.values():
        if existing_user.email == user_in.email or existing_user.username == user_in.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists",
            )
    
    # Create a new user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
    )
    
    # Save the user
    users_db[user_id] = user
    
    # Add user to the role in Casbin
    CasbinEnforcer.add_role_for_user(user.username, user.role)
    CasbinEnforcer.save_policy()
    
    # Generate an access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.id, role=user.role, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }