"""Pytest fixtures and test configuration."""
import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment before importing app modules
os.environ["DATA_DIR"] = str(Path(tempfile.mkdtemp()) / "test_data")
os.environ["DATABASE_URL"] = "sqlite:///test.db"

from app.core.database import Base, get_db
from app.main import app


# Test database
TEST_DB_URL = "sqlite:///test_badminton.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create and tear down test database for each test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    # Clean up test db file
    db_path = Path("test_badminton.db")
    if db_path.exists():
        try:
            db_path.unlink()
        except PermissionError:
            pass


@pytest.fixture
def client():
    """FastAPI test client with test database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def db_session():
    """Direct database session for test setup."""
    db = TestSession()
    try:
        yield db
    finally:
        db.close()
