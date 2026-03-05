import pytest
from app.app import create_app
from app.extensions import db
from sqlalchemy import text

@pytest.fixture(scope="module")
def app():
    app = create_app("testing")
    yield app

def test_db_is_postgresql(app):
    """Vérifie qu'on est bien connecté à PostgreSQL."""
    with app.app_context():
        url = str(db.engine.url)
        assert "postgresql" in url, f"Attendu PostgreSQL, obtenu : {url}"

def test_db_is_test_database(app):
    """Vérifie qu'on tourne sur colors-tests et pas colors-dev."""
    with app.app_context():
        url = str(db.engine.url)
        assert "colors-tests" in url, (
            f"Les tests doivent tourner sur colors-tests, pas sur : {url}"
        )

def test_db_connection_alive(app):
    """Vérifie que la connexion est réellement active."""
    with app.app_context():
        result = db.session.execute(text("SELECT 1")).scalar()
        assert result == 1, "La connexion à la base de données est morte"

def test_db_tables_exist(app):
    """Vérifie que les tables sont bien créées."""
    with app.app_context():
        db.create_all()
        tables = db.inspect(db.engine).get_table_names()
        assert "pictures" in tables or "picture" in tables, (
            f"Table Picture introuvable. Tables présentes : {tables}"
        )
        assert "tags" in tables or "tag" in tables, (
            f"Table Tag introuvable. Tables présentes : {tables}"
        )
