import pytest

from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy import event

from tests.integration.model import Base, Session


@pytest.fixture(scope="session")
def engine(request):
    engine = create_engine("postgresql://localhost:5432/sqlalchemy_pg_fts", echo=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def connection(engine, request):
    connection = engine.connect()
    yield connection
    connection.close()


@pytest.fixture(scope="session")
def setup_db(connection, request):
    Base.metadata.bind = connection
    Base.metadata.create_all()

    def teardown():
        Base.metadata.drop_all()

    request.addfinalizer(teardown)

    return None


@pytest.fixture(autouse=True)
def session(connection, setup_db, request):
    transaction = connection.begin()
    session = Session(bind=connection)
    print("Create transaction")
    session.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(db_session, transaction):
        if transaction.nested and not transaction._parent.nested:
            print("Expire all")
            session.expire_all()
            print("Begin new nested")
            session.begin_nested()

    def teardown():
        Session.remove()
        print("Rollback transaction")
        transaction.rollback()

    request.addfinalizer(teardown)

    return session
