from sqlalchemy import DECIMAL, Boolean, Column, DateTime, ForeignKey, Integer, Interval, String, Text, Time, func
from sqlalchemy.orm import relationship

from dijon.database import Base


class Echo(Base):
    __tablename__ = "echoes"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __unicode__(self):
        return self.username


class ServiceBodyNawsCode(Base):
    __tablename__ = "service_body_naws_codes"

    id = Column(Integer, primary_key=True, index=True)
    root_server_id = Column(ForeignKey("root_servers.id"))
    root_server = relationship("RootServer", uselist=False)
    source_id = Column(Integer)


class ServiceBody(Base):
    __tablename__ = "service_bodies"

    id = Column(Integer, primary_key=True, index=True)
    import_id = Column(ForeignKey("imports.id"))
    import_ = relationship("Import", uselist=False)
    source_id = Column(Integer)

    parent_id = Column(ForeignKey("service_bodies.id"), nullable=True)
    parent = relationship("ServiceBody", remote_side=[id])
    name = Column(String(255))
    type = Column(String(20))
    description = Column(Text, nullable=True)
    url = Column(String(255), nullable=True)
    helpline = Column(String(255), nullable=True)
    world_id = Column(String(20), nullable=True)

    service_body_naws_code_id = Column(ForeignKey("service_body_naws_codes.id"), nullable=True)
    committee_code = relationship("ServiceBodyNawsCode", uselist=False)
    meetings = relationship("Meeting", back_populates="service_body")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Format(Base):
    __tablename__ = "formats"

    id = Column(Integer, primary_key=True, index=True)
    import_id = Column(ForeignKey("imports.id"))
    import_ = relationship("Import", uselist=False)
    source_id = Column(Integer)

    name = Column(String(255))
    key_string = Column(String(255))
    naws_format_code = Column(String(20), nullable=True)
    meetings = relationship("Meeting", secondary="MeetingFormat", backref="Format")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MeetingFormat(Base):
    __tablename__ = "meeting_formats"

    id = Column(Integer, primary_key=True, index=True)

    meeting_id = Column(ForeignKey("meetings.id"))
    format_id = Column(ForeignKey("formats.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MeetingNawsCode(Base):
    __tablename__ = "meeting_naws_codes"

    id = Column(Integer, primary_key=True, index=True)

    root_server_id = Column(ForeignKey("root_servers.id"))
    root_server = relationship("RootServer", uselist=False)
    source_id = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    import_id = Column(ForeignKey("imports.id"))
    import_ = relationship("Import", uselist=False)
    source_id = Column(Integer)

    name = Column(String(255))
    weekday = Column(Integer)
    service_body_id = Column(ForeignKey("service_bodies.id"))
    service_body = relationship("ServiceBody", back_populates="meetings", uselist=False)
    venue_type = Column(Integer, nullable=True)
    start_time = Column(Time)
    duration = Column(Interval)
    time_zone = Column(String(255), nullable=True)
    formats = relationship("Format", secondary="MeetingFormat", backref="Meeting")
    language = Column(String(255), nullable=True)
    latitude = Column(DECIMAL(precision=15, scale=12, asdecimal=True))
    longitude = Column(DECIMAL(precision=15, scale=12, asdecimal=True))
    published = Column(Boolean)
    world_id = Column(String(20), nullable=True)

    meeting_naws_code_id = Column(ForeignKey("meeting_naws_codes.id"), nullable=True)
    committee_code = relationship("MeetingNawsCode", uselist=False)

    location_text = Column(Text, nullable=True)
    location_info = Column(Text, nullable=True)
    location_street = Column(Text, nullable=True)
    location_city_subsection = Column(Text, nullable=True)
    location_neighborhood = Column(Text, nullable=True)
    location_municipality = Column(Text, nullable=True)
    location_sub_province = Column(Text, nullable=True)
    location_province = Column(Text, nullable=True)
    location_postal_code_1 = Column(Text, nullable=True)
    location_nation = Column(Text, nullable=True)
    train_lines = Column(Text, nullable=True)
    bus_lines = Column(Text, nullable=True)
    comments = Column(Text, nullable=True)
    virtual_meeting_link = Column(Text, nullable=True)
    phone_meeting_number = Column(Text, nullable=True)
    virtual_meeting_additional_info = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RootServer(Base):
    __tablename__ = "root_servers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255))
    url = Column(String(255))
    imports = relationship("Import", back_populates="root_server")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Import(Base):
    __tablename__ = "imports"

    id = Column(Integer, primary_key=True, index=True)

    root_server_id = Column(ForeignKey("root_servers.id"))
    root_server = relationship("RootServer", back_populates="imports", uselist=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
