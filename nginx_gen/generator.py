from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import yaml
from .schema import ConfigSpec


def render_nginx_config(spec: ConfigSpec) -> str:
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("nginx.conf.j2")
    return template.render(vhosts=spec.vhosts)


def render_caddy_config(spec: ConfigSpec) -> str:
    template_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("caddyfile.j2")
    return template.render(vhosts=spec.vhosts)


def parse_spec_file(path: str) -> ConfigSpec:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ConfigSpec.model_validate(data)
