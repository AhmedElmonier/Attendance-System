import os
import logging
import ipaddress
from typing import List, Optional
from uuid import UUID

import jwt
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from src.db.connection import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


def _get_current_user_id(request: Request) -> UUID:
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    token = authorization[7:]
    jwt_secret = os.getenv("JWT_SECRET")
    if not jwt_secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"require": ["user_id", "exp"]},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    user_id_str = payload.get("user_id")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Missing user_id claim")
    try:
        return UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user_id in token")


def _get_tenant_id(request: Request) -> UUID:
    tenant_id_str = request.headers.get("X-Tenant-ID")
    if not tenant_id_str:
        raise HTTPException(status_code=400, detail="Missing X-Tenant-ID header")
    try:
        return UUID(tenant_id_str)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid X-Tenant-ID format")


class IpAllowlistSettings(BaseModel):
    enabled: bool = False
    allowed_cidrs: List[str] = Field(default_factory=list)

    @field_validator("allowed_cidrs", mode="before")
    @classmethod
    def validate_cidrs(cls, v):
        if not v:
            return []
        validated = []
        for cidr in v:
            try:
                ipaddress.ip_network(cidr, strict=False)
                validated.append(cidr)
            except ValueError:
                raise ValueError(f"Invalid CIDR block: {cidr}")
        return validated


@router.get("/security/ip-allowlist", response_model=IpAllowlistSettings)
async def get_ip_allowlist(request: Request):
    _get_current_user_id(request)
    tenant_id = _get_tenant_id(request)
    try:
        pool = await get_db()
        rows = await pool.fetch(
            "SELECT cidr_block FROM ip_allowlist WHERE tenant_id = $1",
            tenant_id,
        )
        enabled_row = await pool.fetchrow(
            "SELECT ip_filter_enabled FROM tenant_settings WHERE tenant_id = $1",
            tenant_id,
        )
        enabled = bool(enabled_row["ip_filter_enabled"]) if enabled_row else False
        return {
            "enabled": enabled,
            "allowed_cidrs": [r["cidr_block"] for r in rows],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to load IP allowlist settings")
        raise HTTPException(
            status_code=500, detail="Failed to load IP allowlist settings"
        ) from e


@router.put("/security/ip-allowlist", response_model=IpAllowlistSettings)
async def update_ip_allowlist(payload: IpAllowlistSettings, request: Request):
    _get_current_user_id(request)
    tenant_id = _get_tenant_id(request)
    try:
        pool = await get_db()
        await pool.execute(
            "DELETE FROM ip_allowlist WHERE tenant_id = $1",
            tenant_id,
        )
        if payload.allowed_cidrs:
            await pool.executemany(
                "INSERT INTO ip_allowlist (tenant_id, cidr_block) VALUES ($1, $2)",
                [(tenant_id, cidr) for cidr in payload.allowed_cidrs],
            )
        await pool.execute(
            "INSERT INTO tenant_settings (tenant_id, ip_filter_enabled) VALUES ($1, $2) "
            "ON CONFLICT (tenant_id) DO UPDATE SET ip_filter_enabled = $2",
            tenant_id,
            payload.enabled,
        )
        return {
            "enabled": payload.enabled,
            "allowed_cidrs": payload.allowed_cidrs,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to update IP allowlist settings")
        raise HTTPException(
            status_code=500, detail="Failed to update IP allowlist settings"
        ) from e
