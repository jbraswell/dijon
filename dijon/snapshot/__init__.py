from dijon.snapshot.create import create_snapshot
from dijon.snapshot.diff import diff_snapshots
from dijon.snapshot.get import get_meetings


diff = diff_snapshots
create = create_snapshot


__all__ = ["diff", "create", "get_meetings"]
