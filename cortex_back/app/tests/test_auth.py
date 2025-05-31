# tests/test_auth.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.auth_database import Base, engine

# Fixture para levantar la app y crear tablas
@pytest.fixture(scope="module")
def client():
    # crear tablas de auth en SQLite
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # opcional: limpiar después
    Base.metadata.drop_all(bind=engine)

def test_register_and_login_and_query_log(client):
    # 1) Registro
    user = {"email": "test@prueba.com", "password": "1234abcd"}
    r = client.post("/auth/register", json=user)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == user["email"]
    assert "id" in data

    # 2) Login
    login_data = {"username": user["email"], "password": user["password"]}
    r2 = client.post("/auth/login", data=login_data)
    assert r2.status_code == 200
    token = r2.json().get("access_token")
    assert token

    # 3) Llamada a endpoint protegido
    headers = {"Authorization": f"Bearer {token}"}
    r3 = client.post("/queries/", json={"query_text":"hola mundo"}, headers=headers)
    assert r3.status_code == 200
    q = r3.json()
    assert "id" in q and "timestamp" in q
