from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Verificar que no hay errores fatales
def test_server_arranca_bien():
    response = client.get("/")

    assert response.status_code != 500 # Error de servidor
    assert response.status_code != 404 # Ruta no encontrada

# 2. Proteccion de rutas
def test_rutas_protegidas_requieren_token():
    payload = {
        "nombre_negocio": "Kiosco Test",
        "direccion": "Calle Falsa 123",
        "telefono": "12345678"
    }

    response = client.post("/api/v1/clientes", json=payload, headers={"X-Tennt-ID": "1"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# 3. Login con formato correcto
def test_login_rechaza_json_espera_form_data():
    response = client.post(
        "/api/v1/auth/login/access-token",
        json={"username": "admin", "password": "123"},
        headers={"X-Tenant_ID": "1"}
    )

    assert response.status_code == 422

# 4. Aislamiento multi-tenant 
def test_aislamiento_de_empresa_tenant_requerido():
    headers = {"Authorization": "Bearer fake_token"}

    response = client.get("/api/v1/clientes", headers=headers)

    assert response.status_code == 403