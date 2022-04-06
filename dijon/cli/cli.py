import logging
import os
import sys
from datetime import datetime

import alembic.config
import click
import uvicorn

from dijon import crud, database, snapshot
from dijon.snapshot.create import update_meetings_last_changed


@click.group()
def cli():
    pass


@cli.command()
def create_admin_user():
    logging.basicConfig(level=logging.INFO)
    with database.db_context() as db:
        db_user, created = crud.create_default_admin_user(db)
        if created:
            print(f"Created admin user '{db_user.username}'")
        else:
            print(f"Default admin user '{db_user.username}' already exists")


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
def populate_meeting_last_changed():
    logging.basicConfig(level=logging.INFO)
    with database.db_context() as db:
        for root_server in crud.get_root_servers(db):
            snapshots = crud.get_snapshots(db, root_server.id)
            for snap in snapshots:
                print(f"root_server    {root_server.id}    snapshot    {snap.id}")
                prev_snapshot = crud.get_previous_snapshot(db, snap.id)
                if prev_snapshot:
                    update_meetings_last_changed(db, snap, prev_snapshot)
                    db.commit()


@cli.command()
@click.option("--root-server-id", default=0, show_default=False)
def run_snapshot(root_server_id: int):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('dijon.cli.run_snapshot')
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
            snap = crud.get_snapshot_by_date(db, root_server.id, datetime.utcnow().date())
            if snap is not None:
                logger.info(f"skipping snapshot for {root_server.id}:{root_server.url}")
                continue

            try:
                snapshot.create(db, root_server)
            except Exception:
                # TODO report this somewhere
                logger.exception(f"error creating snapshot for {root_server.id}:{root_server.url}")
                db.rollback()
            else:
                db.commit()


if __name__ == "__main__":
    cli()
