# nginx-config-gen

> Declarative **Nginx** & **Caddy** reverse proxy configuration generator from clean YAML definitions in **Python**.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python)](https://python.org)
[![Nginx](https://img.shields.io/badge/Nginx-Proxy-009639?style=flat-square&logo=nginx)](https://nginx.org)
[![Caddy](https://img.shields.io/badge/Caddy-v2-1F88C0?style=flat-square&logo=caddy)](https://caddyserver.com)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

`#nginx` `#caddy` `#reverse-proxy` `#devops` `#python` `#cli` `#sysadmin` `#automation`

---

## Features

- **Declarative YAML Specs:** Eliminate boilerplate copy-paste and syntax errors in Nginx configs.
- **Built-In Best Practices:** Automatically applies security headers (`X-Frame-Options`, `HSTS`, `nosniff`) and gzip compression.
- **WebSocket Presets:** Simple `websocket: true` flag injects correct `Upgrade` and `Connection` headers.
- **Dual Output Support:** Renders both standard Nginx `server {}` blocks and modern `Caddyfile` syntax.

## Quick Start

```bash
# 1. Install CLI
pip install -r requirements.txt
pip install -e .

# 2. Generate Nginx configuration
nginx-gen generate -f example.spec.yaml -o /etc/nginx/conf.d/app.conf

# 3. Generate Caddyfile
nginx-gen generate -f example.spec.yaml --format=caddy -o /etc/caddy/Caddyfile
```

## Example Spec (`spec.yaml`)

```yaml
version: "1.0"
vhosts:
  - server_name: "api.example.com"
    listen_port: 443
    ssl_enabled: true
    ssl_cert_path: "/etc/ssl/cert.pem"
    ssl_key_path: "/etc/ssl/key.pem"
    locations:
      - path: "/"
        proxy_pass: "http://127.0.0.1:8000"
      - path: "/ws/"
        proxy_pass: "http://127.0.0.1:8000"
        websocket: true
```
