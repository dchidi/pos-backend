from functools import wraps
from pymongo.errors import PyMongoError
from fastapi import HTTPException, status
from app.db.mongodb import mongo  # Assuming mongo.client is initialized

def with_transaction():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not mongo.client:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="MongoDB client is not initialized"
                )
            try:
                async with await mongo.client.start_session() as session:
                    async with session.start_transaction():
                        # Inject session into the wrapped function
                        return await func(*args, session=session, **kwargs)
            except PyMongoError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database transaction failed: {str(e)}"
                )
        return wrapper
    return decorator
