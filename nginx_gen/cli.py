import click
from pathlib import Path
from .generator import parse_spec_file, render_nginx_config, render_caddy_config


@click.group()
def main():
    """Declarative reverse proxy config generator."""
    pass


@main.command()
@click.option("-f", "--file", "spec_file", required=True, type=click.Path(exists=True), help="Path to input YAML spec")
@click.option("-o", "--output", "out_file", type=click.Path(), help="Output file path (default prints to stdout)")
@click.option("--format", "fmt", type=click.Choice(["nginx", "caddy"]), default="nginx", help="Target config syntax")
def generate(spec_file: str, out_file: str, fmt: str):
    """Generate configuration file from YAML spec."""
    spec = parse_spec_file(spec_file)

    if fmt == "caddy":
        result = render_caddy_config(spec)
    else:
        result = render_nginx_config(spec)

    if out_file:
        Path(out_file).write_text(result, encoding="utf-8")
        click.echo(f"Successfully generated {fmt} configuration at {out_file}")
    else:
        click.echo(result)


if __name__ == "__main__":
    main()
