from functools import wraps
from fastapi import Request
from typing import Any, Callable
from src.models.governance import AuditLog
import logging

def audit_log(action: str, entity_type: str):
    """
    Decorator to log administrative actions to the immutable Audit Logs table.
    Expects the FastAPI Request object as the first parameter to extract user context.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Any:
            # 1. Execute the actual endpoint
            response = await func(request, *args, **kwargs)
            
            # 2. Extract Context (Mocked for now, implies JWT decoding in production)
            tenant_id = request.headers.get("X-Tenant-ID", "00000000-0000-0000-0000-000000000000")
            actor_id = request.headers.get("X-User-ID", "00000000-0000-0000-0000-000000000001")
            client_ip = request.client.host if request.client else "unknown"
            
            # 3. Create Audit Record
            # In production, db session would be retrieved from request state.
            audit_entry = AuditLog(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=action,
                entity_type=entity_type,
                ip_address=client_ip,
                # Entity IDs and new values would be extracted from kwargs/response
            )
            
            logging.info(f"AUDIT LOG: {actor_id} performed {action} on {entity_type} from {client_ip}")
            # db.add(audit_entry); db.commit()
            
            return response
        return wrapper
    return decorator
