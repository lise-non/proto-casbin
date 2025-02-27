from typing import Any, Dict, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from ...models.user import User
from ..deps import get_current_user, check_permission

router = APIRouter()

# Simple in-memory resources database
resources_db = {}

@router.get("/", response_model=List[Dict])
def get_resources(
    current_user: User = Depends(check_permission("/resources", "GET"))
) -> Any:
    """
    Get all resources (all users can access this endpoint)
    """
    return list(resources_db.values())

@router.post("/", response_model=Dict)
def create_resource(
    resource: Dict,
    current_user: User = Depends(check_permission("/resources", "POST"))
) -> Any:
    """
    Create a new resource (requires admin or manager role)
    """
    resource_id = str(uuid.uuid4())
    resource_with_id = {**resource, "id": resource_id, "created_by": current_user.username}
    resources_db[resource_id] = resource_with_id
    return resource_with_id

