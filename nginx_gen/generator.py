"""Jinja2 rendering and YAML loading for Nginx and Caddy reverse proxy configs."""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

from .schema import ConfigSpec

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def _zone_name(server_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]+", "_", server_name).strip("_") or "default"


def _render(template_name: str, spec: ConfigSpec) -> str:
    env = Environment(loader=FileSystemLoader(_TEMPLATE_DIR))
    env.filters["zone_name"] = _zone_name
    template = env.get_template(template_name)
    return template.render(vhosts=spec.vhosts)


def render_nginx_config(spec: ConfigSpec) -> str:
    """Render an Nginx configuration string from a validated ConfigSpec."""
    return _render("nginx.conf.j2", spec)


def render_caddy_config(spec: ConfigSpec) -> str:
    """Render a Caddyfile configuration string from a validated ConfigSpec."""
    return _render("caddyfile.j2", spec)


def parse_spec_file(path: str) -> ConfigSpec:
    """Load and validate a YAML specification file."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ConfigSpec.model_validate(data)
