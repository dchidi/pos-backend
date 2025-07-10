from typing import Set, Optional
from fastapi import Request, HTTPException, Depends, status
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_403_FORBIDDEN, HTTP_401_UNAUTHORIZED

from app.core.settings import settings 

from app.models.user import User 
from app.models.role import Role  


bearer_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials  # Extract the raw token from Authorization header
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user = await User.find_one(User.email == payload["sub"])
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
# def require_roles(*allowed_roles: str):
#     async def wrapper(user=Depends(get_current_user)):
#         if user.role not in allowed_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Not authorized"
#             )
#         return user
#     return wrapper

def require_roles(*allowed_roles: str):
    async def wrapper(user=Depends(get_current_user)):
        # If user.role is a single string, convert it to a list for consistency
        user_roles = [user.role] if isinstance(user.role, str) else user.role
        
        # Check if ANY of the user's roles matches the allowed roles
        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        return user
    return wrapper

def require_permissions(*required_permissions: str):
    """
    Checks if user has ANY of the required permissions
    (User model must have permissions: List[str] field)
    """
    async def wrapper(user = Depends(get_current_user)):
        # If user has super_admin, skip check
        if "super_admin" in user.permissions:
            return user
        
        if not any(perm in user.permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires any of: {', '.join(required_permissions)}"
            )
        return user
    return wrapper