from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from dijon.models import (
    Format,
    FormatNawsCode,
    Meeting,
    MeetingFormat,
    MeetingNawsCode,
    RootServer,
    ServiceBody,
    ServiceBodyNawsCode,
    Snapshot,
    Token,
    User,
)
from dijon.settings import settings
from dijon.utils import password_util


# root servers
#
#
def create_root_server(db: Session, name: str, url: str) -> RootServer:
    root_server = RootServer(name=name, url=url)
    db.add(root_server)
    db.flush()
    db.refresh(root_server)
    return root_server


def delete_root_server(db: Session, root_server_id: int) -> bool:
    num_rows = db.query(RootServer).filter(RootServer.id == root_server_id).delete()
    db.flush()
    return num_rows != 0


def get_root_server(db: Session, root_server_id: int) -> Optional[RootServer]:
    return db.query(RootServer).filter(RootServer.id == root_server_id).first()


def get_root_servers(db: Session) -> list[RootServer]:
    return db.query(RootServer).all()


# snapshots
#
#
def create_snapshot(db: Session, root_server: RootServer) -> Snapshot:
    snapshot = Snapshot(root_server_id=root_server.id)
    db.add(snapshot)
    db.flush()
    db.refresh(snapshot)
    return snapshot


def get_snapshot_by_date(db: Session, root_server_id: int, date: date) -> Optional[Snapshot]:
    query = db.query(Snapshot)
    query = query.filter(Snapshot.root_server_id == root_server_id)
    query = query.filter(Snapshot.created_at > date - timedelta(days=1), Snapshot.created_at < date + timedelta(days=1))
    query = query.order_by(desc(Snapshot.created_at))
    return query.first()


def get_nearest_snapshot_by_date(db: Session, root_server_id: int, search_date: date) -> Optional[Snapshot]:
    query = db.query(Snapshot)
    query = query.filter(Snapshot.root_server_id == root_server_id)
    query = query.filter(Snapshot.created_at < search_date + timedelta(days=1))
    query = query.order_by(desc(Snapshot.created_at))
    return query.first()


# service bodies
#
#
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


def get_service_bodies_by_snapshot(db: Session, snapshot_id: int) -> list[ServiceBody]:
    return db.query(ServiceBody).filter(snapshot_id == snapshot_id).all()


def get_service_body_naws_code_by_server(db: Session, root_server_id: int, bmlt_id: int, lock: bool = False) -> Optional[ServiceBodyNawsCode]:
    query = db.query(ServiceBodyNawsCode)
    query = query.filter(ServiceBodyNawsCode.root_server_id == root_server_id, ServiceBodyNawsCode.bmlt_id == bmlt_id)
    if lock:
        query = query.with_for_update()
    return query.first()


def create_service_body_naws_code(db: Session, root_server_id: int, bmlt_id: int, code: str) -> Optional[ServiceBodyNawsCode]:
    naws_code = ServiceBodyNawsCode(root_server_id=root_server_id, bmlt_id=bmlt_id, code=code)
    db.add(naws_code)
    try:
        db.flush()
    except IntegrityError:
        return None
    db.refresh(naws_code)
    query = db.query(ServiceBody)
    query = query.filter(ServiceBody.snapshot.has(root_server_id=root_server_id))
    query = query.filter(ServiceBody.bmlt_id == bmlt_id)
    query.update({"service_body_naws_code_id": naws_code.id}, synchronize_session=False)
    db.flush()
    return naws_code


def delete_service_body_naws_code(db: Session, id: int) -> bool:
    num_rows = db.query(ServiceBodyNawsCode).filter(ServiceBodyNawsCode.id == id).delete()
    db.flush()
    return num_rows != 0


# formats
#
#
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


def get_formats_by_bmlt_ids(db: Session, snapshot_id: int, bmlt_ids: list[int]) -> list[Format]:
    return (
        db.query(Format)
          .filter(Format.snapshot_id == snapshot_id, Format.bmlt_id.in_(bmlt_ids))
          .all()
    )


def get_format_naws_code_by_server(db: Session, root_server_id: int, bmlt_id: int, lock: bool = False) -> Optional[FormatNawsCode]:
    query = db.query(FormatNawsCode)
    query = query.filter(FormatNawsCode.root_server_id == root_server_id, FormatNawsCode.bmlt_id == bmlt_id)
    if lock:
        query = query.with_for_update()
    return query.first()


def create_format_naws_code(db: Session, root_server_id: int, bmlt_id: int, code: str) -> Optional[FormatNawsCode]:
    naws_code = FormatNawsCode(root_server_id=root_server_id, bmlt_id=bmlt_id, code=code)
    db.add(naws_code)
    try:
        db.flush()
    except IntegrityError:
        return None
    db.refresh(naws_code)
    query = db.query(Format)
    query = query.filter(Format.snapshot.has(root_server_id=root_server_id))
    query = query.filter(Format.bmlt_id == bmlt_id)
    query.update({"format_naws_code_id": naws_code.id}, synchronize_session=False)
    db.flush()
    return naws_code


def delete_format_naws_code(db: Session, id: int) -> bool:
    num_rows = db.query(FormatNawsCode).filter(FormatNawsCode.id == id).delete()
    db.flush()
    return num_rows != 0


# meetings
#
#
def get_meeting_naws_codes_by_server(db: Session, root_server_id: int, lock: bool = False) -> list[MeetingNawsCode]:
    query = db.query(MeetingNawsCode)
    query = query.filter(MeetingNawsCode.root_server_id == root_server_id)
    if lock:
        query = query.with_for_update()
    return query.all()


def get_meetings_for_snapshot(db: Session, snapshot_id: int, service_body_bmlt_ids: Optional[list[int]] = None) -> list[Meeting]:
    query = db.query(Meeting).filter(Meeting.snapshot_id == snapshot_id)
    if service_body_bmlt_ids is not None:
        query = query.join(ServiceBody).filter(ServiceBody.bmlt_id.in_(service_body_bmlt_ids))
    query = query.options(selectinload(Meeting.meeting_formats).selectinload(MeetingFormat.format).selectinload(Format.naws_code))
    query = query.options(selectinload(Meeting.service_body).selectinload(ServiceBody.parent).selectinload(ServiceBody.naws_code))
    return query.all()


def create_meeting_naws_code(db: Session, root_server_id: int, bmlt_id: int, code: str) -> Optional[MeetingNawsCode]:
    naws_code = MeetingNawsCode(root_server_id=root_server_id, bmlt_id=bmlt_id, code=code)
    db.add(naws_code)
    try:
        db.flush()
    except IntegrityError:
        return None
    db.refresh(naws_code)
    query = db.query(Meeting)
    query = query.filter(Meeting.snapshot.has(root_server_id=root_server_id))
    query = query.filter(Meeting.bmlt_id == bmlt_id)
    query.update({"meeting_naws_code_id": naws_code.id}, synchronize_session=False)
    db.flush()
    return naws_code


def delete_meeting_naws_code(db: Session, id: int) -> bool:
    num_rows = db.query(MeetingNawsCode).filter(MeetingNawsCode.id == id).delete()
    db.flush()
    return num_rows != 0


# users
#
#
def create_user(db: Session, username: str, email: str, password: str, is_active: bool = True, is_admin: bool = False) -> Optional[User]:
    if db.query(User).filter(User.username == username).first() is not None:
        return None
    hashed_password = password_util.hash(password)
    db_user = User(username=username, email=email, hashed_password=hashed_password, is_active=is_active, is_admin=is_admin)
    db.add(db_user)
    try:
        db.flush()
    except IntegrityError:
        return None
    db.refresh(db_user)
    return db_user


def create_default_admin_user(db: Session) -> tuple[User, bool]:
    db_user = get_user_by_username(db, settings.ADMIN_USERNAME)
    if db_user is None:
        db_user = create_user(db, settings.ADMIN_USERNAME, settings.ADMIN_EMAIL, settings.ADMIN_PASSWORD, is_admin=True)
        print(f"Created admin user '{settings.ADMIN_USERNAME}'")
        return db_user, True
    else:
        print(f"Admin user '{settings.ADMIN_USERNAME}' already exists")
        return db_user, False


def update_user(
    db: Session,
    user_id: int,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_admin: Optional[bool] = None
) -> bool:
    update = {}
    if email is not None:
        update["email"] = email
    if password is not None:
        update["hashed_password"] = password_util.hash(password)
    if is_active is not None:
        update["is_active"] = is_active
    if is_admin is not None:
        update["is_admin"] = is_admin
    db.query(User).filter(User.id == user_id).update(update)
    db.flush()


def delete_user(db: Session, user_id: int):
    num_rows = db.query(User).filter(User.id == user_id).delete()
    db.flush()
    return num_rows != 0


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# token
#
#
def token_exists(db: Session, token: str) -> bool:
    return db.query(Token.id).filter(Token.token == token).first() is not None


def get_token(db: Session, token: str) -> Token:
    return db.query(Token).filter(Token.token == token).first()


def create_token(db: Session, token: str, user_id: int, expires_at: datetime) -> Token:
    token = Token(token=token, user_id=user_id, expires_at=expires_at)
    db.add(token)
    db.flush()
    db.refresh(token)
    return token


def delete_token(db: Session, token: str) -> bool:
    num_rows = db.query(Token).filter(Token.token == token).delete()
    db.flush()
    return num_rows != 0


def delete_expired_tokens(db: Session):
    # give them a day of leeway...
    yesterday = datetime.utcnow() - timedelta(days=1)
    db.query(Token).filter(Token.expires_at < yesterday).delete()
    db.flush()
