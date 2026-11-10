"""CLI entrypoint for Nginx and Caddy reverse proxy config generation."""

from pathlib import Path

import click

from .generator import parse_spec_file, render_caddy_config, render_nginx_config


@click.group()
def main() -> None:
    """Declarative reverse proxy config generator."""


@main.command()
@click.option(
    "-f",
    "--file",
    "spec_file",
    required=True,
    type=click.Path(exists=True),
    help="Path to input YAML spec",
)
@click.option(
    "-o",
    "--output",
    "out_file",
    type=click.Path(),
    help="Output file path (default prints to stdout)",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["nginx", "caddy"]),
    default="nginx",
    help="Target config syntax",
)
def generate(spec_file: str, out_file: str | None, fmt: str) -> None:
    """Generate configuration file from YAML spec."""
    spec = parse_spec_file(spec_file)
    result = render_caddy_config(spec) if fmt == "caddy" else render_nginx_config(spec)

    if out_file:
        Path(out_file).write_text(result, encoding="utf-8")
        click.echo(f"Successfully generated {fmt} configuration at {out_file}")
    else:
        click.echo(result)


if __name__ == "__main__":
    main()
