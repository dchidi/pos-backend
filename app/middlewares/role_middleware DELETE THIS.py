from fastapi import Request, HTTPException
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN
from app.core.settings import settings 

class RoleMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, required_roles: list[str]):
        super().__init__(app)
        self.required_roles = required_roles
        self.public_paths = [
            "/api/v1/users",        # registration
            "/api/v1/auth/login",   
            "/api/v1/auth/verify",
            "/docs", "/openapi.json"
        ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
       

        if any(path.startswith(p) for p in self.public_paths) and request.method in ["GET", "POST"]:
            return await call_next(request)

        token = request.headers.get("Authorization")
        if not token or not token.startswith("Bearer "):
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Not authenticated")

        token = token.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            role = payload.get("role")
            if role not in self.required_roles:
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Insufficient role permissions")
        except JWTError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid token")

        return await call_next(request)
