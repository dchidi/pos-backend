from beanie import PydanticObjectId
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.models.user_setup.user import User
from app.models.blacklisted_token import BlacklistedToken 
from app.models.user_setup.tenant import Tenant
from app.models.logs import Log


from app.services.exceptions import  ValidationError, UnAuthorized, NotFoundError
from app.services.auth.token import decode_token
from fastapi import Request

from app.constants import LogLevel
from app.core.audit_log import audit_log_bg

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



async def get_current_company(token: str = Depends(oauth2_scheme)) -> PydanticObjectId:
    try:
        payload = decode_token(token)
    except JWTError:
        raise ValidationError("Invalid token")
    except Exception:
        raise
    
    company_id = payload.get("company_id")
    if not company_id:
        raise ValidationError("User not assigned to a company")
    
    try:
        oid = PydanticObjectId(company_id)
    except Exception:
        raise ValidationError("Invalid company identifier")
    
    tenant = await Tenant.find_one({"_id": oid})
    if not tenant:
        raise NotFoundError("Tenant not found")
    return oid

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> PydanticObjectId:
    try:
        payload = decode_token(token)
    except JWTError:
        raise ValidationError("Invalid token")
    except Exception:
        raise
    
    user_id = payload.get("sub")
    if not user_id:
        raise ValidationError("Invalid token")
    
    try:
        oid = PydanticObjectId(user_id)
    except Exception:
        raise ValidationError("Invalid user identifier")

    return oid 

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
     # 1. Check if token is blacklisted
    if await BlacklistedToken.find_one({"token": token}):
        raise UnAuthorized("Token revoked")

    # 2. Decode token and extract user ID
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise UnAuthorized("Invalid token. User ID not found.")

    # 3. Lookup user by ID
    user = await User.get(user_id)
    if not user:
        raise UnAuthorized("User not found")
    
    if not user.company_id:
            raise ValidationError("User not assigned to a company")

    return user

async def get_current_token(token: str = Depends(oauth2_scheme)) -> str:
    return token


def require_permission(permission: str):
    async def dependency(current_user: User = Depends(get_current_user)):
        if permission not in current_user.permissions:
            raise UnAuthorized(f"Missing permission: {permission}")
        return current_user
    return dependency


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
            raise UnAuthorized( f"Requires any of: {', '.join(required_permissions)}" )
        return user
    return wrapper

# usage:
# Depends(require_roles_or_permissions("admin", "user:create","*"))
def require_roles_or_permissions(*allowed: str):
    async def checker(current_user: User = Depends(get_current_user), request: Request = None):
        # App Administrator only
        if "*" in current_user.permissions:
            return current_user.id

        # Check normal permissions and roles
        if not any((p in current_user.permissions) or (current_user.role == p) for p in allowed):            
            audit_log_bg(request, LogLevel.SECURITY, exc="You do not have the required privileges")
            raise UnAuthorized("You do not have the required privileges")

        return current_user.id
    return checker