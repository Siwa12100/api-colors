import pytest
from app.app import create_app
from app.extensions import db
from app.models.users import User
from app.models.workspace import WorkSpace
from app.models.datasource import DataSource
from app.models.picture import Picture, OrientationEnum
from app.models.folder import Folder


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

# --- helpers ---

def create_user(overrides={}):
    defaults = {"email": "test@test.com", "full_name": "Test User", "role": "user", "is_active": True}
    user = User(**{**defaults, **overrides})
    db.session.add(user)
    db.session.commit()
    return user.id

def create_workspace(user_id, overrides={}):
    defaults = {
        "user_id": user_id,
        "name": "Mon Workspace",
        "isSystem": False,
        "favorites": [],
        "sources": [],
    }
    ws = WorkSpace(**{**defaults, **overrides})
    db.session.add(ws)
    db.session.commit()
    return ws.id

def create_datasource(overrides={}):
    defaults = {"name": "GOOGLE_DRIVE", "link": "https://drive.google.com", "type": "CLOUD_STORAGE"}
    ds = DataSource(**{**defaults, **overrides})
    db.session.add(ds)
    db.session.commit()
    return ds.id

def create_picture(datasource_id, overrides={}):
    defaults = {
        "google_id": "abc123",
        "name": "sunset.jpg",
        "comment": "Beautiful sunset",
        "mainColors": [],
        "orientation": OrientationEnum.LANDSCAPE,
        "ratio": 0,
        "resolutionX": 1920,
        "resolutionY": 1080,
        "contrast": 0,
        "luminosity": 0,
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

def create_folder(workspace_id, overrides={}):
    defaults = {"name": "Mon Folder", "workspace_id": workspace_id, "parent_folder_id": None}
    folder = Folder(**{**defaults, **overrides})
    db.session.add(folder)
    db.session.commit()
    return folder.id


# ---------- GET all ----------

def test_get_workspaces_missing_user_id(client):
    resp = client.get("/api/workspaces")
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_get_workspaces_user_not_found(client):
    resp = client.get("/api/workspaces?user_id=9999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()

def test_get_workspaces_creates_default_if_empty(client):
    user_id = create_user()
    resp = client.get(f"/api/workspaces?user_id={user_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    assert data["data"][0]["name"] == "Mon Workspace"
    assert data["data"][0]["isSystem"] == True

def test_get_workspaces_default_has_all_sources(client):
    user_id = create_user()
    ds_id = create_datasource()
    resp = client.get(f"/api/workspaces?user_id={user_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert ds_id in data["data"][0]["sources"]

def test_get_workspaces_returns_existing(client):
    user_id = create_user()
    create_workspace(user_id, {"name": "Workspace 1"})
    create_workspace(user_id, {"name": "Workspace 2"})
    resp = client.get(f"/api/workspaces?user_id={user_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 2

def test_get_workspaces_pagination(client):
    user_id = create_user()
    for i in range(5):
        create_workspace(user_id, {"name": f"Workspace {i}"})
    resp = client.get(f"/api/workspaces?user_id={user_id}&page=1&per_page=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 5
    assert len(data["data"]) == 2
    assert data["pages"] == 3


# ---------- GET one ----------

def test_get_workspace(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    resp = client.get(f"/api/workspaces/{ws_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == ws_id
    assert data["user_id"] == user_id

def test_get_workspace_not_found(client):
    resp = client.get("/api/workspaces/9999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


# ---------- GET pictures ----------

def test_get_workspace_pictures_empty_sources(client):
    user_id = create_user()
    ws_id = create_workspace(user_id, {"sources": []})
    resp = client.get(f"/api/workspaces/{ws_id}/pictures")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["data"] == []
    assert data["total"] == 0

def test_get_workspace_pictures(client):
    user_id = create_user()
    ds_id = create_datasource()
    ws_id = create_workspace(user_id, {"sources": [ds_id]})
    create_picture(ds_id)
    create_picture(ds_id, {"google_id": "id2", "name": "mountain.jpg"})
    resp = client.get(f"/api/workspaces/{ws_id}/pictures")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 2

def test_get_workspace_pictures_filters_by_source(client):
    user_id = create_user()
    ds1_id = create_datasource({"name": "SOURCE_1"})
    ds2_id = create_datasource({"name": "SOURCE_2"})
    ws_id = create_workspace(user_id, {"sources": [ds1_id]})
    create_picture(ds1_id, {"google_id": "id1"})
    create_picture(ds2_id, {"google_id": "id2"})
    resp = client.get(f"/api/workspaces/{ws_id}/pictures")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1

def test_get_workspace_pictures_not_found(client):
    resp = client.get("/api/workspaces/9999/pictures")
    assert resp.status_code == 404

def test_get_workspace_pictures_pagination(client):
    user_id = create_user()
    ds_id = create_datasource()
    ws_id = create_workspace(user_id, {"sources": [ds_id]})
    for i in range(5):
        create_picture(ds_id, {"google_id": f"id{i}", "name": f"pic{i}.jpg"})
    resp = client.get(f"/api/workspaces/{ws_id}/pictures?page=1&per_page=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 5
    assert len(data["data"]) == 2
    assert data["pages"] == 3


# ---------- GET folders ----------

def test_get_workspace_folders_empty(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    resp = client.get(f"/api/workspaces/{ws_id}/folders")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 0
    assert data["data"] == []

def test_get_workspace_folders(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    create_folder(ws_id, {"name": "Folder 1"})
    create_folder(ws_id, {"name": "Folder 2"})
    resp = client.get(f"/api/workspaces/{ws_id}/folders")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 2

def test_get_workspace_folders_only_root(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    root_id = create_folder(ws_id, {"name": "Root"})
    create_folder(ws_id, {"name": "Child", "parent_folder_id": root_id})
    resp = client.get(f"/api/workspaces/{ws_id}/folders")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1
    assert data["data"][0]["name"] == "Root"

def test_get_workspace_folders_not_found(client):
    resp = client.get("/api/workspaces/9999/folders")
    assert resp.status_code == 404


# ---------- PUT ----------

def test_update_workspace_name(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    resp = client.put(f"/api/workspaces/{ws_id}", json={"name": "Nouveau Nom"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Nouveau Nom"

def test_update_workspace_sources(client):
    user_id = create_user()
    ds_id = create_datasource()
    ws_id = create_workspace(user_id)
    resp = client.put(f"/api/workspaces/{ws_id}", json={"sources": [ds_id]})
    assert resp.status_code == 200
    assert ds_id in resp.get_json()["sources"]

def test_update_workspace_favorites(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    resp = client.put(f"/api/workspaces/{ws_id}", json={"favorites": [1, 2, 3]})
    assert resp.status_code == 200
    assert resp.get_json()["favorites"] == [1, 2, 3]

def test_update_workspace_partial(client):
    user_id = create_user()
    ws_id = create_workspace(user_id, {"name": "Original"})
    resp = client.put(f"/api/workspaces/{ws_id}", json={"favorites": [1]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Original"
    assert data["favorites"] == [1]

def test_update_workspace_not_found(client):
    resp = client.put("/api/workspaces/9999", json={"name": "ghost"})
    assert resp.status_code == 404

def test_update_workspace_invalid_body(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    resp = client.put(f"/api/workspaces/{ws_id}", data="not json", content_type="text/plain")
    assert resp.status_code == 415