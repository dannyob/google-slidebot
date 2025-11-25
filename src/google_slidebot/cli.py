"""Command-line interface for google-slidebot."""

import click


@click.group()
@click.version_option()
def cli():
    """A Python CLI application"""
    pass


@cli.command()
def hello():
    """Say hello."""
    click.echo("Hello from google-slidebot!")


if __name__ == "__main__":
    cli()
