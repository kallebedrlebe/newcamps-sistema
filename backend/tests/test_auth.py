def test_login_sucesso(client, admin_token):
    assert admin_token is not None

def test_login_senha_errada(client):
    resp = client.post("/auth/login", json={"email": "admin@test.com", "password": "errada"})
    assert resp.status_code == 401

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
