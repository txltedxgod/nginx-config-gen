"""Tests for reverse proxy YAML parsing, validation guards, Nginx/Caddy rendering, and CLI."""

from pathlib import Path

import pytest
from click.testing import CliRunner
from pydantic import ValidationError

from nginx_gen.cli import main as cli_main
from nginx_gen.generator import parse_spec_file, render_caddy_config, render_nginx_config
from nginx_gen.schema import ConfigSpec


def test_parse_and_render_nginx_and_caddy(tmp_path: Path) -> None:
    spec_content = """
    version: "1.0"
    vhosts:
      - server_name: "test.dev"
        listen_port: 443
        ssl_enabled: true
        ssl_cert_path: "/etc/certs/test.pem"
        ssl_key_path: "/etc/certs/test.key"
        rate_limit_per_minute: 120
        locations:
          - path: "/"
            proxy_pass: "http://localhost:3000"
            websocket: true
    """
    spec_file = tmp_path / "spec.yaml"
    spec_file.write_text(spec_content, encoding="utf-8")

    spec = parse_spec_file(str(spec_file))
    nginx_conf = render_nginx_config(spec)
    assert "server_name test.dev;" in nginx_conf
    assert "ssl_certificate /etc/certs/test.pem;" in nginx_conf
    assert "limit_req_zone $binary_remote_addr zone=test_dev_rl:10m rate=120r/m;" in nginx_conf
    assert "proxy_pass http://localhost:3000;" in nginx_conf
    assert "proxy_set_header Upgrade $http_upgrade;" in nginx_conf

    caddy_conf = render_caddy_config(spec)
    assert "test.dev {" in caddy_conf
    assert "reverse_proxy localhost:3000" in caddy_conf


def test_schema_blocks_missing_ssl_paths_and_directive_injection() -> None:
    with pytest.raises(ValidationError):
        ConfigSpec.model_validate(
            {
                "vhosts": [
                    {
                        "server_name": "secure.dev",
                        "ssl_enabled": True,
                        "locations": [{"proxy_pass": "http://127.0.0.1:8000"}],
                    }
                ]
            }
        )

    with pytest.raises(ValidationError):
        ConfigSpec.model_validate(
            {
                "vhosts": [
                    {
                        "server_name": "evil.dev; return 200 pwned",
                        "locations": [{"proxy_pass": "http://127.0.0.1:8000"}],
                    }
                ]
            }
        )


def test_cli_generate_command(tmp_path: Path) -> None:
    spec_file = tmp_path / "app.yaml"
    out_file = tmp_path / "Caddyfile"
    spec_file.write_text(
        """
vhosts:
  - server_name: "app.example.org"
    locations:
      - path: "/api"
        proxy_pass: "http://127.0.0.1:9000"
""",
        encoding="utf-8",
    )
    runner = CliRunner()
    res = runner.invoke(
        cli_main, ["generate", "-f", str(spec_file), "-o", str(out_file), "--format", "caddy"]
    )
    assert res.exit_code == 0
    assert "reverse_proxy 127.0.0.1:9000" in out_file.read_text(encoding="utf-8")
