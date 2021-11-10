from sqlalchemy.orm import Session

from dijon import models


def create_echo(db: Session, message: str) -> models.Echo:
    echo = models.Echo(message=message)
    db.add(echo)
    db.flush()
    db.refresh(echo)
    return echo
