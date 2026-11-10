"""Pydantic v2 schema and directive-injection guards for reverse proxy specifications."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator, model_validator

_UNSAFE_DIRECTIVE_RE = re.compile(r"[;{}\r\n]")


def _reject_unsafe_chars(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty.")
    if _UNSAFE_DIRECTIVE_RE.search(cleaned):
        raise ValueError(f"{field_name} contains unsafe directive characters (; {{ }} newline).")
    return cleaned


class UpstreamLocation(BaseModel):
    """HTTP location routing rule."""

    path: str = Field(default="/", description="URL path matching prefix")
    proxy_pass: str = Field(
        ..., description="Target backend address (e.g. http://127.0.0.1:8000)"
    )
    websocket: bool = Field(default=False, description="Enable WebSocket upgrade headers")
    client_max_body_size_mb: int = Field(
        default=10, ge=1, le=10240, description="Max allowed upload size in MB"
    )
    cache_enabled: bool = Field(default=False, description="Enable proxy caching")

    @field_validator("path", "proxy_pass")
    @classmethod
    def validate_safe_strings(cls, v: str, info) -> str:
        return _reject_unsafe_chars(v, info.field_name)


class VirtualHost(BaseModel):
    """Virtual host specification for Nginx and Caddy generation."""

    server_name: str = Field(..., description="Domain name (e.g. api.example.com)")
    listen_port: int = Field(default=80, ge=1, le=65535, description="HTTP listen port")
    ssl_enabled: bool = Field(default=False, description="Enable HTTPS/SSL")
    ssl_cert_path: str | None = None
    ssl_key_path: str | None = None
    hsts_enabled: bool = Field(default=True, description="Enforce Strict-Transport-Security")
    gzip_enabled: bool = Field(
        default=True, description="Enable gzip compression for text/json/js"
    )
    rate_limit_per_minute: int | None = Field(
        default=None, ge=1, description="Requests per minute rate limit"
    )
    locations: list[UpstreamLocation] = Field(default_factory=list, min_length=1)

    @field_validator("server_name")
    @classmethod
    def validate_server_name(cls, v: str) -> str:
        return _reject_unsafe_chars(v, "server_name")

    @field_validator("ssl_cert_path", "ssl_key_path")
    @classmethod
    def validate_ssl_paths(cls, v: str | None, info) -> str | None:
        if v is None:
            return None
        return _reject_unsafe_chars(v, info.field_name)

    @model_validator(mode="after")
    def require_ssl_cert_and_key(self) -> VirtualHost:
        if self.ssl_enabled and (not self.ssl_cert_path or not self.ssl_key_path):
            raise ValueError("ssl_cert_path and ssl_key_path are required when ssl_enabled=True.")
        return self


class ConfigSpec(BaseModel):
    """Top-level declarative proxy configuration document."""

    version: str = "1.0"
    vhosts: list[VirtualHost] = Field(..., min_length=1)
