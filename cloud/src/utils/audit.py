from functools import wraps
from typing import Any, Callable
from uuid import UUID
from starlette.requests import Request
import logging

logger = logging.getLogger(__name__)


def audit_log(action: str, entity_type: str):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            response = await func(*args, **kwargs)

            req: Request | None = kwargs.get("request")
            if req is None:
                for arg in args:
                    if isinstance(arg, Request):
                        req = arg
                        break

            if req is None:
                logger.warning(
                    f"Cannot audit {action} on {entity_type}: Request not found"
                )
                return response

            tenant_id_str = req.headers.get("X-Tenant-ID", "")
            actor_id_str = req.headers.get("X-User-ID", "")

            try:
                tenant_id = UUID(tenant_id_str)
            except (ValueError, TypeError):
                logger.warning(
                    f"Audit skipped: invalid tenant_id header '{tenant_id_str}'"
                )
                return response

            try:
                actor_id = UUID(actor_id_str)
            except (ValueError, TypeError):
                logger.warning(
                    f"Audit skipped: invalid actor_id header '{actor_id_str}'"
                )
                return response

            client_ip = "unknown"
            if req.client is not None:
                client_ip = req.client.host

            from src.models.governance import AuditLog

            audit_entry = AuditLog(
                tenant_id=tenant_id,
                actor_id=actor_id,
                action=action,
                entity_type=entity_type,
                ip_address=client_ip,
            )

            try:
                db = getattr(req.state, "db", None)
                if db is not None:
                    db.add(audit_entry)
                    db.commit()
                else:
                    logger.warning(
                        f"Audit entry not persisted (no DB session): "
                        f"{actor_id} performed {action} on {entity_type}"
                    )
            except Exception:
                logger.exception(
                    f"Failed to persist audit log for {actor_id} {action} on {entity_type}"
                )

            logger.info(
                f"AUDIT: {actor_id} performed {action} on {entity_type} from {client_ip}"
            )
            return response

        return wrapper

    return decorator
