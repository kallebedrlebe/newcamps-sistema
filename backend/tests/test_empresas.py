def test_criar_empresa(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.post("/empresas/", json={
        "razao_social": "Empresa Teste Ltda",
        "cnpj": "11222333000181",
    }, headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["cnpj"] == "11222333000181"

def test_cnpj_duplicado(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {"razao_social": "Empresa A", "cnpj": "11222333000181"}
    client.post("/empresas/", json=payload, headers=headers)
    resp = client.post("/empresas/", json=payload, headers=headers)
    assert resp.status_code == 409

def test_listar_empresas(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/empresas/", headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
