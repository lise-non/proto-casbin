from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from typing import Callable, Optional
from starlette.middleware.base import BaseHTTPMiddleware

from ...config import settings
from ...core.casbin_rbac import CasbinEnforcer

class AuthorizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for checking if the user has permission to access the resource.
    This is an alternative to using the check_permission dependency.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip authorization for auth endpoints
        if request.url.path.startswith(f"{settings.API_PREFIX}/auth"):
            return await call_next(request)
        
        # Get authorization header
        authorization = request.headers.get("Authorization")
        if not authorization:
            return await call_next(request)
        
        # Extract token
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return await call_next(request)
        except ValueError:
            return await call_next(request)
        
        # Decode token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get("sub")
            role = payload.get("role")
            
            if not username or not role:
                return await call_next(request)
                
        except JWTError:
            return await call_next(request)
        
        # Check if user has permission to access the resource
        path = request.url.path
        method = request.method
        
        enforcer = CasbinEnforcer.get_instance()
        has_permission = enforcer.enforce(username, path, method)
        
        if not has_permission:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Not enough permissions"}
            )
        
        # Continue processing the request
        return await call_next(request)