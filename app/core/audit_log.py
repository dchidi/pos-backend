from fastapi import Request
from app.models.logs import Log
from app.constants import LogLevel
from app.services.auth.dependencies import decode_token
import asyncio


async def audit_log(request:Request, log_level:LogLevel, exc: str):
    try:
        user_id = None
        auth_header = request.headers.get("authorization")
        
        if auth_header and " " in auth_header:
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token)
                user_id = str(payload.get("sub")) if payload.get("sub") else None                
            except Exception:
                # Invalid token, just keep user_id = None
                pass
            
        await Log(
            user_id=user_id,
            endpoint=str(request.url),
            action=str(request.method),
            level=log_level,
            details={
                "error_msg": str(exc),
                "headers": {k: str(v)[:100] for k,v in request.headers.items()},
                "query_params": {k: str(v)[:200] for k,v in request.query_params.items()},
                "client_host": request.client.host
            }
        ).insert()
    except Exception as log_exc:
        print(log_exc)

# Runs in background 
def audit_log_bg(request: Request, log_level: LogLevel, exc: str):
    asyncio.create_task(audit_log(request, log_level, exc))