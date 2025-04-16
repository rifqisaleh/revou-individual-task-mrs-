import pytest
from app import create_app, db
from flask_jwt_extended import create_access_token

@pytest.fixture
def test_app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DEBUG": True,  
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "JWT_SECRET_KEY": "test-secret",
    })


    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(test_app):
    return test_app.test_client()
