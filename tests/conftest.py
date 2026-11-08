import pytest
from subsystem3 import create_app

@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.sqlite3"
    app = create_app({"TESTING": True, "DATABASE": str(db_path), "SECRET_KEY": "test"})
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()
