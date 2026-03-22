import ipaddress
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class IPFilterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_allowed_ips_func):
        super().__init__(app)
        self.get_allowed_ips = get_allowed_ips_func

    def _get_client_ip(self, request: Request) -> str:
        if request.client is not None:
            return request.client.host
        x_forwarded = request.headers.get("X-Forwarded-For")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return "unknown"

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if "/api/v1/governance" in path or "/api/v1/admin" in path:
            tenant_id = request.headers.get("X-Tenant-ID")
            if not tenant_id:
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Access forbidden: X-Tenant-ID header required."
                    },
                )

            client_ip_str = self._get_client_ip(request)
            try:
                client_ip = ipaddress.ip_address(client_ip_str)
            except ValueError:
                logger.warning(f"Invalid client IP: {client_ip_str}")
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Access forbidden: invalid client IP."},
                )

            try:
                allowed_cidrs, is_enabled = await self.get_allowed_ips(tenant_id)
            except Exception:
                logger.error(f"Failed to retrieve allow-list for tenant {tenant_id}")
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Access forbidden: failed to verify IP allow-list."
                    },
                )

            if is_enabled and allowed_cidrs:
                valid_networks = []
                for cidr in allowed_cidrs:
                    try:
                        valid_networks.append(ipaddress.ip_network(cidr, strict=False))
                    except ValueError:
                        logger.warning(f"Ignoring malformed CIDR: {cidr}")

                if valid_networks:
                    is_allowed = any(client_ip in network for network in valid_networks)
                    if not is_allowed:
                        return JSONResponse(
                            status_code=403,
                            content={
                                "detail": "Access forbidden: IP address not in allow-list."
                            },
                        )

        response = await call_next(request)
        return response
