import pytest
from app.app import create_app
from app.extensions import db
from app.models.datasource import DataSource
from app.models.picture import Picture, OrientationEnum
from app.models.tag import Tag

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(autouse=True)
def app_ctx(app):
    with app.app_context():
        yield

@pytest.fixture(autouse=True)
def clean_db():
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def datasource():
    ds = DataSource(name="drive-test", link="http://test", type="CLOUD_STORAGE")
    db.session.add(ds)
    db.session.commit()
    return ds.id

# --- helpers ---

def create_picture(datasource_id, overrides={}):
    defaults = {
        "google_id": "abc123",
        "name": "sunset.jpg",
        "comment": "Beautiful sunset",
        "mainColors": ["FF5733", "C70039"],
        "orientation": OrientationEnum.LANDSCAPE,
        "ratio": 16,
        "resolutionX": 1920,
        "resolutionY": 1080,
        "contrast": 80,
        "luminosity": 70,
        "thumbnailLink": "https://example.com/thumb.jpg",
        "downloadLink": "https://example.com/download.jpg",
        "lastUpdated": "2024-01-01T00:00:00Z",
        "datasource_id": datasource_id,
        "tags": [],
    }
    pic = Picture()
    pic.create(**{**defaults, **overrides})
    db.session.add(pic)
    db.session.commit()
    return pic.id

def create_tag(overrides={}):
    defaults = {"name": "Nature", "hex_code": "#00FF00"}
    tag = Tag()
    tag.create(**{**defaults, **overrides})
    db.session.add(tag)
    db.session.commit()
    return tag.id


# ---------- GET all ----------

def test_get_pictures_empty(client):
    resp = client.get("/api/pictures")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 0
    assert data["data"] == []

def test_get_pictures(client, datasource):
    create_picture(datasource)
    resp = client.get("/api/pictures")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    assert len(data["data"]) == 1

def test_get_pictures_pagination(client, datasource):
    for i in range(5):
        create_picture(datasource, {"google_id": f"id{i}", "name": f"pic{i}.jpg"})
    resp = client.get("/api/pictures?page=1&per_page=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 5
    assert len(data["data"]) == 2
    assert data["pages"] == 3

def test_get_pictures_filter_name(client, datasource):
    create_picture(datasource, {"google_id": "id1", "name": "sunset.jpg"})
    create_picture(datasource, {"google_id": "id2", "name": "mountain.jpg"})
    resp = client.get("/api/pictures?name=sunset")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    assert data["data"][0]["name"] == "sunset.jpg"

def test_get_pictures_filter_orientation(client, datasource):
    create_picture(datasource, {"google_id": "id1", "orientation": OrientationEnum.LANDSCAPE})
    create_picture(datasource, {"google_id": "id2", "orientation": OrientationEnum.PORTRAIT, "resolutionX": 1080, "resolutionY": 1920})
    resp = client.get("/api/pictures?orientation=landscape")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1

def test_get_pictures_filter_resolution(client, datasource):
    create_picture(datasource, {"google_id": "id1", "resolutionX": 1920, "resolutionY": 1080})
    create_picture(datasource, {"google_id": "id2", "resolutionX": 800, "resolutionY": 600})
    resp = client.get("/api/pictures?min_width=1000")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    assert data["data"][0]["name"] == "sunset.jpg"


# ---------- GET one ----------

def test_get_single_picture(client, datasource):
    picture_id = create_picture(datasource)
    resp = client.get(f"/api/pictures/{picture_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "sunset.jpg"
    assert data["google_id"] == "abc123"

def test_get_picture_not_found(client):
    resp = client.get("/api/pictures/9999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


# ---------- PUT ----------

def test_update_picture_name(client, datasource):
    picture_id = create_picture(datasource)
    resp = client.put(f"/api/pictures/{picture_id}", json={"name": "new_name.jpg"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "new_name.jpg"

def test_update_picture_comment(client, datasource):
    picture_id = create_picture(datasource)
    resp = client.put(f"/api/pictures/{picture_id}", json={"comment": "Updated comment"})
    assert resp.status_code == 200
    assert resp.get_json()["comment"] == "Updated comment"

def test_update_picture_partial(client, datasource):
    picture_id = create_picture(datasource)
    resp = client.put(f"/api/pictures/{picture_id}", json={"name": "renamed.jpg"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "renamed.jpg"
    assert data["comment"] == "Beautiful sunset"

def test_update_picture_tags(client, datasource):
    tag_id = create_tag()
    picture_id = create_picture(datasource)
    resp = client.put(f"/api/pictures/{picture_id}", json={"tags": [tag_id]})
    assert resp.status_code == 200
    tags = resp.get_json()["tags"]
    assert len(tags) == 1
    assert tags[0]["id"] == tag_id

def test_update_picture_tags_replace(client, datasource):
    tag1_id = create_tag({"name": "Tag1", "hex_code": "#111111"})
    tag2_id = create_tag({"name": "Tag2", "hex_code": "#222222"})
    picture_id = create_picture(datasource)
    client.put(f"/api/pictures/{picture_id}", json={"tags": [tag1_id]})
    resp = client.put(f"/api/pictures/{picture_id}", json={"tags": [tag2_id]})
    assert resp.status_code == 200
    tags = resp.get_json()["tags"]
    assert len(tags) == 1
    assert tags[0]["id"] == tag2_id

def test_update_picture_tags_clear(client, datasource):
    tag_id = create_tag()
    picture_id = create_picture(datasource)
    client.put(f"/api/pictures/{picture_id}", json={"tags": [tag_id]})
    resp = client.put(f"/api/pictures/{picture_id}", json={"tags": []})
    assert resp.status_code == 200
    assert resp.get_json()["tags"] == []

def test_update_picture_invalid_tag(client, datasource):
    picture_id = create_picture(datasource)
    resp = client.put(f"/api/pictures/{picture_id}", json={"tags": [9999]})
    assert resp.status_code == 200
    assert resp.get_json()["tags"] == []

def test_update_picture_not_found(client):
    resp = client.put("/api/pictures/9999", json={"name": "ghost.jpg"})
    assert resp.status_code == 404

def test_update_picture_invalid_body(client, datasource):
    picture_id = create_picture(datasource)
    resp = client.put(f"/api/pictures/{picture_id}", data="not json", content_type="text/plain")
    assert resp.status_code == 415