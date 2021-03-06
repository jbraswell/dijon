import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from dijon.crud import create_default_admin_user
from dijon.database import Base
from dijon.dependencies import get_db
from dijon.main import app
from dijon.settings import settings
from dijon.utils.token_util import create_access_token


def get_db_url():
    db_user = settings.get("DBUSER", "root")
    db_pass = settings.get("DBPASSWORD", "dijon")
    db_host = settings.get("DBHOST", "0.0.0.0")
    db_port = settings.get("DBPORT", 3306)
    db_name = settings.get("DBNAME", "dijontest")
    return f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"


class Ctx:
    def __init__(self, db: Session, client: TestClient):
        self.db = db
        self.client = client


@pytest.fixture(scope="session")
def engine():
    global _access_token
    engine = create_engine(get_db_url())
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)
    Base.metadata.create_all(bind=engine)
    with sessionmaker(autocommit=False, autoflush=False, bind=engine)() as session:
        admin_user, _ = create_default_admin_user(session)
        _access_token = create_access_token(session, admin_user)
        session.commit()
    yield engine


# creating lots of access tokens gets slow, so we just make one here
# that all of the tests can use
_access_token = None


@pytest.fixture(scope="session")
def admin_access_token(engine):
    return _access_token


@pytest.fixture
def db(engine):
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def ctx(db: Session):
    client = TestClient(app)
    try:
        app.dependency_overrides[get_db] = lambda: (yield db)
        yield Ctx(db, client)
    finally:
        app.dependency_overrides[get_db] = get_db
