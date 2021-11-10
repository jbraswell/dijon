from sqlalchemy import Column, DateTime, Integer, String, func

from dijon.database import Base


class Echo(Base):
    __tablename__ = "echoes"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __unicode__(self):
        return self.username
