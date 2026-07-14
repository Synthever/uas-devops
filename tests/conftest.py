"""Pytest configuration and fixtures."""
import sys
import os
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import create_app
from app.models import db as _db


@pytest.fixture
def app():
    """Create test application."""
    app = create_app(testing=True)
    yield app


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def db(app):
    """Database session for testing."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()
