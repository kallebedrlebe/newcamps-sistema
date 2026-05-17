import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models.user import User
from app.services.auth_service import hash_password

TEST_DB = "sqlite:///./test.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    db = TestSession()
    user = User(nome="Admin", email="admin@test.com", senha_hash=hash_password("admin123"), is_admin=True)
    db.add(user)
    db.commit()
    db.close()
    resp = client.post("/auth/login", json={"email": "admin@test.com", "password": "admin123"})
    return resp.json()["access_token"]
