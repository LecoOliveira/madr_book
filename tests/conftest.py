import factory
import factory.fuzzy
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from madr_book.app import app
from madr_book.database import create_engine, get_session
from madr_book.models import Livros, Romancistas, User, table_registry
from madr_book.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}senha')


class LivroFactory(factory.Factory):
    class Meta:
        model = Livros

    ano = factory.Faker('year')
    titulo = factory.Faker('name')
    autor_id = 1


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
def engine():
    with PostgresContainer('postgres:16', driver='psycopg') as postgres:
        _engine = create_engine(postgres.get_connection_url())

        with _engine.begin():
            yield _engine


@pytest.fixture
def session(engine):
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session):
    pwd = 'testtest'
    user = UserFactory(password=get_password_hash(pwd))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = pwd

    return user


@pytest.fixture
def other_user(session):
    user = UserFactory()

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def romancista(session):
    romancista_ = Romancistas(nome="test romancista")
    session.add(romancista_)
    session.commit()
    session.refresh(romancista_)

    return romancista_


@pytest.fixture
def livro(session, romancista):
    livro = Livros(ano=1999, titulo="Teste livro", autor_id=romancista.id)
    session.add(livro)
    session.commit()

    return livro
