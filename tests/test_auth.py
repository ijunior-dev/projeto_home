def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_token(client):
    response = client.post("/auth/token", data={"username": "admin", "password": "123456"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_senha_errada(client):
    response = client.post("/auth/token", data={"username": "admin", "password": "errada"})
    assert response.status_code == 401


def test_login_usuario_inexistente(client):
    response = client.post("/auth/token", data={"username": "naoexiste", "password": "123456"})
    assert response.status_code == 401


def test_rota_protegida(client):
    login = client.post("/auth/token", data={"username": "admin", "password": "123456"})
    token = login.json()["access_token"]
    response = client.get("/protegida", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "mensagem" in response.json()


def test_rota_protegida_sem_token(client):
    response = client.get("/protegida")
    assert response.status_code == 401


def test_refresh_token(client):
    login = client.post("/auth/token", data={"username": "admin", "password": "123456"})
    refresh_token = login.json()["refresh_token"]
    response = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body  # rotação de token


def test_refresh_com_access_token_deve_falhar(client):
    login = client.post("/auth/token", data={"username": "admin", "password": "123456"})
    access_token = login.json()["access_token"]
    response = client.post("/auth/refresh", json={"refresh_token": access_token})
    assert response.status_code == 401
