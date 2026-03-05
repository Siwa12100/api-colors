import pytest
from app.app import create_app
from app.extensions import db
from app.models.user import User
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
    defaults = {"user_id": user_id, "name": "Mon Workspace", "isSystem": False, "favorites": [], "sources": []}
    ws = WorkSpace(**{**defaults, **overrides})
    db.session.add(ws)
    db.session.commit()
    return ws.id

def create_folder(workspace_id, overrides={}):
    defaults = {"name": "Mon Folder", "workspace_id": workspace_id, "parent_folder_id": None}
    folder = Folder(**{**defaults, **overrides})
    db.session.add(folder)
    db.session.commit()
    return folder.id

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
        "comment": None,
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


# ---------- GET one ----------

def test_get_folder(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    resp = client.get(f"/api/folders/{folder_id}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["id"] == folder_id
    assert data["workspace_id"] == ws_id

def test_get_folder_not_found(client):
    resp = client.get("/api/folders/9999")
    assert resp.status_code == 404
    assert "error" in resp.get_json()


# ---------- GET pictures ----------

def test_get_folder_pictures_empty(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    resp = client.get(f"/api/folders/{folder_id}/pictures")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 0
    assert data["data"] == []

def test_get_folder_pictures(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    ds_id = create_datasource()
    pic_id = create_picture(ds_id)

    # Associe la picture au folder
    folder = db.session.get(Folder, folder_id)
    picture = db.session.get(Picture, pic_id)
    folder.pictures.append(picture)
    db.session.commit()

    resp = client.get(f"/api/folders/{folder_id}/pictures")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 1

def test_get_folder_pictures_pagination(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    ds_id = create_datasource()

    folder = db.session.get(Folder, folder_id)
    for i in range(5):
        pic_id = create_picture(ds_id, {"google_id": f"id{i}", "name": f"pic{i}.jpg"})
        folder.pictures.append(db.session.get(Picture, pic_id))
    db.session.commit()

    resp = client.get(f"/api/folders/{folder_id}/pictures?page=1&per_page=2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 5
    assert len(data["data"]) == 2
    assert data["pages"] == 3

def test_get_folder_pictures_not_found(client):
    resp = client.get("/api/folders/9999/pictures")
    assert resp.status_code == 404


# ---------- GET children folders ----------

def test_get_children_folders_empty(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    resp = client.get(f"/api/folders/{folder_id}/folders")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 0
    assert data["data"] == []

def test_get_children_folders(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    parent_id = create_folder(ws_id, {"name": "Parent"})
    create_folder(ws_id, {"name": "Child 1", "parent_folder_id": parent_id})
    create_folder(ws_id, {"name": "Child 2", "parent_folder_id": parent_id})
    resp = client.get(f"/api/folders/{parent_id}/folders")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total"] == 2

def test_get_children_folders_not_found(client):
    resp = client.get("/api/folders/9999/folders")
    assert resp.status_code == 404


# ---------- POST ----------

def test_create_folder(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    resp = client.post("/api/folders", json={"name": "Nouveau Folder", "workspace_id": ws_id})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Nouveau Folder"
    assert data["workspace_id"] == ws_id
    assert data["parent_folder_id"] is None

def test_create_folder_with_parent(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    parent_id = create_folder(ws_id, {"name": "Parent"})
    resp = client.post("/api/folders", json={"name": "Child", "workspace_id": ws_id, "parent_folder_id": parent_id})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["parent_folder_id"] == parent_id

def test_create_folder_missing_fields(client):
    resp = client.post("/api/folders", json={"name": "Sans workspace"})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_create_folder_workspace_not_found(client):
    resp = client.post("/api/folders", json={"name": "Folder", "workspace_id": 9999})
    assert resp.status_code == 404

def test_create_folder_parent_not_found(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    resp = client.post("/api/folders", json={"name": "Folder", "workspace_id": ws_id, "parent_folder_id": 9999})
    assert resp.status_code == 404

def test_create_folder_parent_wrong_workspace(client):
    user_id = create_user()
    ws1_id = create_workspace(user_id, {"name": "Workspace 1"})
    ws2_id = create_workspace(user_id, {"name": "Workspace 2"})
    parent_id = create_folder(ws1_id, {"name": "Parent"})
    resp = client.post("/api/folders", json={"name": "Child", "workspace_id": ws2_id, "parent_folder_id": parent_id})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_create_folder_duplicate(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    client.post("/api/folders", json={"name": "Folder", "workspace_id": ws_id})
    resp = client.post("/api/folders", json={"name": "Folder", "workspace_id": ws_id})
    assert resp.status_code == 409

def test_create_folder_invalid_body(client):
    resp = client.post("/api/folders", data="not json", content_type="text/plain")
    assert resp.status_code == 415


# ---------- PUT ----------

def test_update_folder_name(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    resp = client.put(f"/api/folders/{folder_id}", json={"name": "Nouveau Nom"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Nouveau Nom"

def test_update_folder_add_pictures(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    ds_id = create_datasource()
    pic_id = create_picture(ds_id)

    resp = client.put(f"/api/folders/{folder_id}", json={"pictures": [pic_id]})
    assert resp.status_code == 200
    assert pic_id in resp.get_json()["pictures"]

def test_update_folder_replace_pictures(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    ds_id = create_datasource()
    pic1_id = create_picture(ds_id, {"google_id": "id1"})
    pic2_id = create_picture(ds_id, {"google_id": "id2"})

    client.put(f"/api/folders/{folder_id}", json={"pictures": [pic1_id]})
    resp = client.put(f"/api/folders/{folder_id}", json={"pictures": [pic2_id]})
    assert resp.status_code == 200
    pictures = resp.get_json()["pictures"]
    assert pic1_id not in pictures
    assert pic2_id in pictures

def test_update_folder_clear_pictures(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    ds_id = create_datasource()
    pic_id = create_picture(ds_id)

    client.put(f"/api/folders/{folder_id}", json={"pictures": [pic_id]})
    resp = client.put(f"/api/folders/{folder_id}", json={"pictures": []})
    assert resp.status_code == 200
    assert resp.get_json()["pictures"] == []

def test_update_folder_invalid_picture_id(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)

    resp = client.put(f"/api/folders/{folder_id}", json={"pictures": [9999]})
    assert resp.status_code == 200
    assert resp.get_json()["pictures"] == []  # id inexistant ignoré

def test_update_folder_name_and_pictures(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    ds_id = create_datasource()
    pic_id = create_picture(ds_id)

    resp = client.put(f"/api/folders/{folder_id}", json={"name": "Nouveau Nom", "pictures": [pic_id]})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == "Nouveau Nom"
    assert pic_id in data["pictures"]

def test_update_folder_not_found(client):
    resp = client.put("/api/folders/9999", json={"name": "ghost"})
    assert resp.status_code == 404

def test_update_folder_invalid_body(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    resp = client.put(f"/api/folders/{folder_id}", data="not json", content_type="text/plain")
    assert resp.status_code == 415


# ---------- DELETE ----------

def test_delete_folder(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    folder_id = create_folder(ws_id)
    resp = client.delete(f"/api/folders/{folder_id}")
    assert resp.status_code == 200
    assert "supprimé" in resp.get_json()["message"]

def test_delete_folder_cascades_children(client):
    user_id = create_user()
    ws_id = create_workspace(user_id)
    parent_id = create_folder(ws_id, {"name": "Parent"})
    child_id = create_folder(ws_id, {"name": "Child", "parent_folder_id": parent_id})
    client.delete(f"/api/folders/{parent_id}")
    resp = client.get(f"/api/folders/{child_id}")
    assert resp.status_code == 404

def test_delete_folder_not_found(client):
    resp = client.delete("/api/folders/9999")
    assert resp.status_code == 404