import os

import alembic.config
import click
import uvicorn


@click.group()
def cli():
    pass


@cli.command()
def ping():
    print("pong")


@cli.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8000)
def run_api(host, port):
    uvicorn.run("dijon.main:app", host=host, port=port)


@cli.command()
def run_migrations():
    old_cwd = os.getcwd()
    new_cwd = os.path.join(os.path.dirname(__file__), "..")
    os.chdir(new_cwd)
    alembic.config.main(argv=["--raiseerr", "upgrade", "head"])
    os.chdir(old_cwd)


if __name__ == "__main__":
    cli()
