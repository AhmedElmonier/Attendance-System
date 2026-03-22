import ipaddress
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class IPFilterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, get_allowed_ips_func):
        super().__init__(app)
        self.get_allowed_ips = get_allowed_ips_func

    async def dispatch(self, request: Request, call_next):
        # We only protect specific admin/governance routes based on configuration
        path = request.url.path
        if "/api/v1/governance" in path or "/api/v1/admin" in path:
            client_ip = request.client.host
            tenant_id = request.headers.get("X-Tenant-ID")
            
            if tenant_id:
                allowed_cidrs, is_enabled = await self.get_allowed_ips(tenant_id)
                if is_enabled and allowed_cidrs:
                    ip_obj = ipaddress.ip_address(client_ip)
                    is_allowed = any(ip_obj in ipaddress.ip_network(cidr) for cidr in allowed_cidrs)
                    
                    if not is_allowed:
                        return JSONResponse(
                            status_code=403,
                            content={"detail": "Access forbidden: IP address not in allow-list."}
                        )

        response = await call_next(request)
        return response
