# Serve para testar health check, login, refresh token e acesso a rota protegida.

from fastapi.testclient import TestClient
from app.main import app

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