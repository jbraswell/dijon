from typing import Optional

from sqlalchemy.orm import Session

from dijon.models import (
    Echo,
    Format,
    FormatNawsCode,
    Meeting,
    MeetingNawsCode,
    RootServer,
    ServiceBody,
    ServiceBodyNawsCode,
    Snapshot,
)


class DoesNotExist(Exception):
    pass


def create_echo(db: Session, message: str) -> Echo:
    echo = Echo(message=message)
    db.add(echo)
    db.flush()
    db.refresh(echo)
    return echo


def create_snapshot(db: Session, root_server: RootServer) -> Snapshot:
    snapshot = Snapshot(root_server_id=root_server.id)
    db.add(snapshot)
    db.flush()
    db.refresh(snapshot)
    return snapshot


def create_service_body(
    db: Session,
    snapshot_id: int,
    bmlt_id: int,
    name: str,
    type: str,
    parent_id: int = None,
    description: str = None,
    url: str = None,
    helpline: str = None,
    world_id: str = None
) -> ServiceBody:
    service_body = ServiceBody(
        snapshot_id=snapshot_id,
        bmlt_id=bmlt_id,
        name=name,
        type=type,
        parent_id=parent_id,
        description=description,
        url=url,
        helpline=helpline,
        world_id=world_id,
    )
    db.add(service_body)
    db.flush()
    db.refresh(service_body)
    return service_body


def create_format(db: Session, snapshot_id: int, bmlt_id: int, key_string: str, name: str = None, world_id: str = None) -> Format:
    format = Format(
        snapshot_id=snapshot_id,
        bmlt_id=bmlt_id,
        key_string=key_string,
        name=name,
        world_id=world_id,
    )
    db.add(format)
    db.flush()
    db.refresh(format)
    return format


def create_root_server(db: Session, name: str, url: str) -> RootServer:
    root_server = RootServer(name=name, url=url)
    db.add(root_server)
    db.flush()
    db.refresh(root_server)
    return root_server


def get_root_server(db: Session, root_server_id: int) -> Optional[RootServer]:
    return db.query(RootServer).filter(RootServer.id == root_server_id).first()


def get_root_servers(db: Session) -> list[RootServer]:
    return db.query(RootServer).all()


def get_meeting_by_snapshot(db: Session, snapshot_id: int, bmlt_id: int) -> Optional[Meeting]:
    return (
        db.query(Meeting)
          .filter(Meeting.snapshot_id == snapshot_id, Meeting.bmlt_id == bmlt_id)
          .first()
    )


def get_service_body_by_snapshot(db: Session, snapshot_id: int, bmlt_id: int) -> Optional[ServiceBody]:
    return (
        db.query(ServiceBody)
          .filter(ServiceBody.snapshot_id == snapshot_id, ServiceBody.bmlt_id == bmlt_id)
          .first()
    )


def get_formats_by_snapshot(db: Session, snapshot_id: int, bmlt_ids: list[int]) -> list[Format]:
    return (
        db.query(Format)
          .filter(Format.snapshot_id == snapshot_id, Format.bmlt_id.in_(bmlt_ids))
          .all()
    )


def get_service_body_naws_code_by_server(db: Session, root_server_id: int, bmlt_id: int) -> Optional[ServiceBodyNawsCode]:
    return (
        db.query(ServiceBodyNawsCode)
          .filter(ServiceBodyNawsCode.root_server_id == root_server_id, ServiceBodyNawsCode.bmlt_id == bmlt_id)
          .first()
    )


def get_format_naws_code_by_server(db: Session, root_server_id: int, bmlt_id: int) -> Optional[FormatNawsCode]:
    return (
        db.query(FormatNawsCode)
          .filter(FormatNawsCode.root_server_id == root_server_id, FormatNawsCode.bmlt_id == bmlt_id)
          .first()
    )


def get_meeting_naws_code_by_server(db: Session, root_server_id: int, bmlt_id: int) -> Optional[MeetingNawsCode]:
    return (
        db.query(MeetingNawsCode)
          .filter(MeetingNawsCode.root_server_id == root_server_id, MeetingNawsCode.bmlt_id == bmlt_id)
          .first()
    )
