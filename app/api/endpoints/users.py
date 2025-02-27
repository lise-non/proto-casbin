from typing import Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from ...core.security import get_password_hash
from ...models.user import users_db, User
from ...schemas.user import User as UserSchema, UserCreate, UserUpdate
from ..deps import get_current_user, check_permission
from ...core.casbin_rbac import CasbinEnforcer

router = APIRouter()

@router.get("/", response_model=List[UserSchema])
def get_users(
    current_user: User = Depends(check_permission("/users", "GET"))
) -> Any:
    """
    Get all users (requires admin or manager role)
    """
    return list(users_db.values())

@router.post("/", response_model=UserSchema)
def create_user(
    user_in: UserCreate,
    current_user: User = Depends(check_permission("/users", "POST"))
) -> Any:
    """
    Create a new user (requires admin role)
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
    
    return user

@router.get("/{user_id}", response_model=UserSchema)
def get_user(
    user_id: str,
    current_user: User = Depends(check_permission("/users", "GET"))
) -> Any:
    """
    Get a user by ID (requires admin or manager role)
    """
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: str,
    user_in: UserUpdate,
    current_user: User = Depends(check_permission("/users", "PUT"))
) -> Any:
    """
    Update a user (requires admin role)
    """
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user fields
    user_data = user.dict()
    
    for field, value in user_in.dict(exclude_unset=True).items():
        if field == "password" and value:
            user_data["hashed_password"] = get_password_hash(value)
        else:
            user_data[field] = value
    
    # Create updated user
    updated_user = User(**user_data)
    
    # Update user in the database
    users_db[user_id] = updated_user
    
    # Update role in Casbin if it has changed
    if user_in.role and user_in.role != user.role:
        CasbinEnforcer.delete_role_for_user(user.username, user.role)
        CasbinEnforcer.add_role_for_user(updated_user.username, updated_user.role)
        CasbinEnforcer.save_policy()
    
    return updated_user

@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    user_id: str,
    current_user: User = Depends(check_permission("/users", "DELETE"))
) -> Any:
    """
    Delete a user (requires admin role)
    """
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user = users_db[user_id]
    
    # Delete user from Casbin
    for role in CasbinEnforcer.get_roles_for_user(user.username):
        CasbinEnforcer.delete_role_for_user(user.username, role)
    
    # Delete user from the database
    deleted_user = users_db.pop(user_id)
    
    # Save Casbin policy
    CasbinEnforcer.save_policy()
    
    return deleted_user

@router.get("/me", response_model=UserSchema)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information
    """
    return current_user

@router.put("/me", response_model=UserSchema)
def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update current user information
    """
    # Update user fields
    user_data = current_user.dict()
    
    for field, value in user_in.dict(exclude_unset=True, exclude={"role"}).items():
        if field == "password" and value:
            user_data["hashed_password"] = get_password_hash(value)
        else:
            user_data[field] = value
    
    # Create updated user
    updated_user = User(**user_data)
    
    # Update user in the database
    users_db[current_user.id] = updated_user
    
    return updated_user