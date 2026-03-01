import pytest
from app.app import create_app
from app.extensions import db

TEST_DATABASE_URL = "postgresql://colors:lasangatechnasuslaflord'albespin@localhost:5432/colors-tests"

@pytest.fixture(scope="session", autouse=True)
def app():
    """Crée l'app une seule fois pour toute la session."""
    app = create_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = TEST_DATABASE_URL
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(autouse=True)
def clean_db(app):
    """Vide toutes les tables avant chaque test."""
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

SAMPLE_COLOR = {
    "name": "Rouge",
    "hex_code": "#FF0000",
    "rgb_r": 255,
    "rgb_g": 0,
    "rgb_b": 0,
}

def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Colors API"

def test_create_color(client):
    resp = client.post("/api/colors", json=SAMPLE_COLOR)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Rouge"
    assert data["hex_code"] == "#FF0000"

def test_get_colors(client):
    client.post("/api/colors", json=SAMPLE_COLOR)
    resp = client.get("/api/colors")
    assert resp.status_code == 200
    assert resp.get_json()["total"] == 1

def test_get_single_color(client):
    client.post("/api/colors", json=SAMPLE_COLOR)
    resp = client.get("/api/colors/1")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Rouge"

def test_update_color(client):
    client.post("/api/colors", json=SAMPLE_COLOR)
    updated = {**SAMPLE_COLOR, "name": "Rouge Foncé", "hex_code": "#CC0000"}
    resp = client.put("/api/colors/1", json=updated)
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Rouge Foncé"

def test_delete_color(client):
    client.post("/api/colors", json=SAMPLE_COLOR)
    resp = client.delete("/api/colors/1")
    assert resp.status_code == 200
    resp = client.get("/api/colors/1")
    assert resp.status_code == 404

def test_create_invalid_color(client):
    resp = client.post("/api/colors", json={"name": "Bad"})
    assert resp.status_code == 400

def test_duplicate_color(client):
    client.post("/api/colors", json=SAMPLE_COLOR)
    resp = client.post("/api/colors", json=SAMPLE_COLOR)
    assert resp.status_code == 409
