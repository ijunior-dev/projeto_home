# Serve para testar health check, login, refresh token e acesso a rota protegida.

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.models import User
from app.security import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def seed_test_user():
    db = TestingSessionLocal()
    existing_user = db.query(User).filter(User.username == "admin").first()
    if not existing_user:
        user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("123456"),
            is_active=True
        )
        db.add(user)
        db.commit()
    db.close()

seed_test_user()

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_login_token():
    response = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "123456"
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

def test_rota_protegida():
    login_response = client.post(
        "/auth/token",
        data={
            "username": "admin",
            "password": "123456"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = client.get(
        "/protegida",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "mensagem" in response.json()