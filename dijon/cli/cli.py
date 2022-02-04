import logging
import os
import sys

import alembic.config
import click
import uvicorn
from dynaconf import settings

from dijon import crud, database, snapshot


logging.basicConfig(level=logging.INFO)


@click.group()
def cli():
    pass


@cli.command()
def create_admin_user():
    with database.db_context() as db:
        db_user = crud.get_user_by_username(db, settings.ADMIN_USERNAME)
        if db_user is None:
            crud.create_user(db, settings.ADMIN_USERNAME, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD, is_admin=True)
            print(f"Created admin user '{settings.ADMIN_USERNAME}'")
        else:
            print(f"Admin user '{settings.ADMIN_USERNAME}' already exists")


@cli.command()
@click.option("--host", default="127.0.0.1")
@click.option("--port", default=8000)
def run_api(host: str, port: int):
    uvicorn.run("dijon.main:app", host=host, port=port)


@cli.command()
def run_migrations():
    old_cwd = os.getcwd()
    new_cwd = os.path.join(os.path.dirname(__file__), "..")
    os.chdir(new_cwd)
    alembic.config.main(argv=["--raiseerr", "upgrade", "head"])
    os.chdir(old_cwd)


@cli.command()
@click.option("--root-server-id", default=0, show_default=False)
def run_snapshot(root_server_id: int):
    with database.db_context() as db:
        if root_server_id:
            root_server = crud.get_root_server(db, root_server_id)
            if not root_server:
                print(f"Error: root_server with id {root_server_id} does not exist")
                sys.exit(1)
            root_servers = [root_server]
        else:
            root_servers = crud.get_root_servers(db)

        for root_server in root_servers:
            snapshot.create_snapshot(db, root_server)
            db.commit()


if __name__ == "__main__":
    cli()
