from typing import Optional

from sqlalchemy.orm import Session

from dijon import crud, models


class SnapshotCache:
    def __init__(self, db: Session, snapshot: models.Snapshot):
        self._db = db
        self._snapshot = snapshot
        self._service_bodies: Optional[dict[int, models.ServiceBody]] = None
        self._meeting_naws_codes: Optional[dict[int, models.MeetingNawsCode]] = None
        self._naws_code_cache = NawsCodeCache(db, snapshot.root_server)

    @property
    def snapshot(self) -> models.Snapshot:
        return self._snapshot

    @property
    def service_bodies(self) -> dict[int, models.ServiceBody]:
        if self._service_bodies is None:
            db_sbs = crud.get_service_bodies_by_snapshot(self._db, self._snapshot.id)
            db_sb_dict = {db_sb.bmlt_id: db_sb for db_sb in db_sbs}
            self._service_bodies = db_sb_dict
        return self._service_bodies

    def get_service_body(self, bmlt_id: int) -> Optional[models.ServiceBody]:
        return self.service_bodies.get(bmlt_id)

    def get_meeting_naws_code(self, bmlt_id: int) -> Optional[models.MeetingNawsCode]:
        return self._naws_code_cache.get_meeting_naws_code.get(bmlt_id)

    def clear(self):
        self._service_bodies = None
        self._meeting_naws_codes = None


class NawsCodeCache:
    def __init__(self, db: Session, root_server: models.RootServer):
        self._db = db
        self._root_server = root_server
        self._meeting_naws_codes: Optional[dict[int, models.MeetingNawsCode]] = None
        self._service_body_naws_codes: Optional[dict[int, models.ServiceBodyNawsCode]] = None
        self._format_naws_codes: Optional[dict[int, models.FormatNawsCode]] = None

    @property
    def meeting_naws_codes(self) -> dict[int, models.MeetingNawsCode]:
        if self._meeting_naws_codes is None:
            naws_codes = crud.get_meeting_naws_codes_by_server(self._db, self._root_server.id)
            self._meeting_naws_codes = {nc.bmlt_id: nc for nc in naws_codes}
        return self._meeting_naws_codes

    @property
    def service_body_naws_codes(self) -> dict[int, models.ServiceBodyNawsCode]:
        if self._service_body_naws_codes is None:
            naws_codes = crud.get_service_body_naws_codes_by_server(self._db, self._root_server.id)
            self._service_body_naws_codes = {nc.bmlt_id: nc for nc in naws_codes}
        return self._service_body_naws_codes

    @property
    def format_naws_codes(self) -> dict[int, models.FormatNawsCode]:
        if self._format_naws_codes is None:
            naws_codes = crud.get_format_naws_codes_by_server(self._db, self._root_server.id)
            self._format_naws_codes = {nc.bmlt_id: nc for nc in naws_codes}
        return self._format_naws_codes

    def get_meeting_naws_code(self, bmlt_id: int) -> Optional[models.MeetingNawsCode]:
        return self.meeting_naws_codes.get(bmlt_id)

    def get_service_body_naws_code(self, bmlt_id: int) -> Optional[models.ServiceBodyNawsCode]:
        return self.service_body_naws_codes.get(bmlt_id)

    def get_format_naws_code(self, bmlt_id: int) -> Optional[models.FormatNawsCode]:
        return self.format_naws_codes.get(bmlt_id)

    def clear(self):
        self._meeting_naws_codes = None
        self._service_body_naws_codes = None
        self._format_naws_codes = None
