from dijon.snapshot.create import create_snapshot
from dijon.snapshot.diff import diff_snapshots
from dijon.snapshot.get import get_formats, get_meetings, get_service_bodies


diff = diff_snapshots
create = create_snapshot


__all__ = ["diff", "create", "get_formats", "get_meetings", "get_service_bodies"]
