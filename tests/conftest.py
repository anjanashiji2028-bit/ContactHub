import os
import tempfile
import pytest
from app import create_app
from config import TestConfig
from database.init_db import init_db, get_db_connection
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    """Create and configure a clean temporary Flask application instance for each test."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    class RuntimeTestConfig(TestConfig):
        DATABASE_PATH = db_path
        TESTING = True
        WTF_CSRF_ENABLED = False  # Disable CSRF in tests for direct POST assertions

    flask_app = create_app(RuntimeTestConfig)

    with flask_app.app_context():
        init_db(db_path)
        # Pre-seed a test user and a second isolated user
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
            ("Alice Smith", "alice@test.local", generate_password_hash("Secret@123"))
        )
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)",
            ("Bob Jones", "bob@test.local", generate_password_hash("Secret@456"))
        )
        conn.commit()
        conn.close()

    yield flask_app

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Test client logged in as Alice Smith."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['user_name'] = "Alice Smith"
        sess['user_email'] = "alice@test.local"
    return client
