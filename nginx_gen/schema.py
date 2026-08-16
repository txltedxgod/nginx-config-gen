from typing import List, Optional
from pydantic import BaseModel, Field


class UpstreamLocation(BaseModel):
    path: str = Field(default="/", description="URL path matching prefix")
    proxy_pass: str = Field(..., description="Target backend address (e.g. http://127.0.0.1:8000)")
    websocket: bool = Field(default=False, description="Enable WebSocket upgrade headers")
    client_max_body_size_mb: int = Field(default=10, description="Max allowed upload size in MB")
    cache_enabled: bool = Field(default=False, description="Enable proxy caching")


class VirtualHost(BaseModel):
    server_name: str = Field(..., description="Domain name (e.g. api.example.com)")
    listen_port: int = Field(default=80, description="HTTP listen port")
    ssl_enabled: bool = Field(default=false, description="Enable HTTPS/SSL")
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    hsts_enabled: bool = Field(default=True, description="Enforce Strict-Transport-Security")
    gzip_enabled: bool = Field(default=True, description="Enable gzip compression for text/json/js")
    rate_limit_per_minute: Optional[int] = Field(default=None, description="Requests per minute rate limit")
    locations: List[UpstreamLocation] = Field(default_factory=list)


class ConfigSpec(BaseModel):
    version: str = "1.0"
    vhosts: List[VirtualHost]
