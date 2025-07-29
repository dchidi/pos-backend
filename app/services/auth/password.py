from passlib.context import CryptContext
from beanie import PydanticObjectId

from app.models.user_setup.user import User

from app.services.crud_services import CRUD
from app.services.auth import create_access_token, create_refresh_token

from app.services.exceptions import InvalidCredentials

crud = CRUD(User)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

async def reset_password(
    password: str,
    user_id: PydanticObjectId,
    company_id: PydanticObjectId
) -> str:
    
    user = await crud.update(user_id, company_id, 
        {"hashed_password": pwd_context.hash(password), "reset_password":False}
    )
    if not user:
        raise InvalidCredentials("Invalid credentials")
    access_token = create_access_token(subject=user.id, company_id=user.company_id)
    refresh_token = create_refresh_token(subject=user.id, company_id=user.company_id)
    return access_token, refresh_token
