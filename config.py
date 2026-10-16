import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'contacthub-dev-insecure-secret-key-replace-in-production')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'database', 'contacthub.db'))
    TESTING = False
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    ITEMS_PER_PAGE = 8
    APP_VERSION = "1.0.0"
    APP_NAME = "ContactHub"

class TestConfig(Config):
    TESTING = True
    DEBUG = True
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'test_contacthub.db')
    SECRET_KEY = 'test-secret-key-not-for-production'
    WTF_CSRF_ENABLED = False
