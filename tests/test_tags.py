import pytest
from app.app import create_app
from app.extensions import db

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

SAMPLE_TAG = {
    "name": "Nature",
    "hex_code": "#00FF00",
}

def test_create_tag(client):
    resp = client.post("/api/tags", json=SAMPLE_TAG)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Nature"
    assert data["hex_code"] == "#00FF00"

def test_get_tags(client):
    client.post("/api/tags", json=SAMPLE_TAG)
    resp = client.get("/api/tags")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    assert len(data["data"]) == 1

def test_get_tags_pagination(client):
    for i in range(5):
        client.post("/api/tags", json={"name": f"Tag{i}", "hex_code": "#000000"})
    resp = client.get("/api/tags?page=1&per_page=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 5
    assert len(data["data"]) == 2
    assert data["pages"] == 3

def test_get_single_tag(client):
    post_resp = client.post("/api/tags", json=SAMPLE_TAG)
    tag_id = post_resp.get_json()["id"]
    resp = client.get(f"/api/tags/{tag_id}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Nature"

def test_get_tag_not_found(client):
    resp = client.get("/api/tags/9999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()

def test_update_tag(client):
    post_resp = client.post("/api/tags", json=SAMPLE_TAG)
    tag_id = post_resp.get_json()["id"]
    resp = client.put(f"/api/tags/{tag_id}", json={"name": "Urban", "hex_code": "#123456"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Urban"
    assert data["hex_code"] == "#123456"

def test_update_tag_partial(client):
    post_resp = client.post("/api/tags", json=SAMPLE_TAG)
    tag_id = post_resp.get_json()["id"]
    resp = client.put(f"/api/tags/{tag_id}", json={"name": "Forêt"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Forêt"
    assert data["hex_code"] == "#00FF00"  # inchangé

def test_update_tag_not_found(client):
    resp = client.put("/api/tags/9999", json={"name": "Ghost"})
    assert resp.status_code == 404

def test_delete_tag(client):
    post_resp = client.post("/api/tags", json=SAMPLE_TAG)
    tag_id = post_resp.get_json()["id"]
    resp = client.delete(f"/api/tags/{tag_id}")
    assert resp.status_code == 200
    resp = client.get(f"/api/tags/{tag_id}")
    assert resp.status_code == 404

def test_delete_tag_not_found(client):
    resp = client.delete("/api/tags/9999")
    assert resp.status_code == 404

def test_create_tag_missing_fields(client):
    resp = client.post("/api/tags", json={"name": "Incomplet"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_create_tag_invalid_body(client):
    resp = client.post("/api/tags", data="not json", content_type="text/plain")
    assert resp.status_code == 415

def test_create_duplicate_tag(client):
    client.post("/api/tags", json=SAMPLE_TAG)
    resp = client.post("/api/tags", json=SAMPLE_TAG)
    assert resp.status_code == 409
    assert "error" in resp.get_json()