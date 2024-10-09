import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app import models, schemas
from app.database import Base

SQLALCHEMY_DATABASE_URL = "postgresql://default:AwRbcNPl27Vu@ep-white-sound-a4mg0y4l.us-east-1.aws.neon.tech:5432/verceldb?sslmode=require"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_recycle=3600, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """ Setup and teardown for the entire test suite. """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client():
    """ Provides a test client for FastAPI. """
    with TestClient(app) as c:
        yield c

def test_create_user(client):
    data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "name": "Test User"
    }
    response = client.post("/users/", json=data)
    assert response.status_code == 201
    assert response.json()["email"] == "testuser@example.com"
    assert response.json()["username"] == "testuser"
    assert "id" in response.json()

def test_read_users(client):
    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0

def test_read_user(client):
    data = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "name": "Test User 2"
    }
    create_response = client.post("/users/", json=data)
    user_id = create_response.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "testuser2@example.com"
    assert response.json()["username"] == "testuser2"

def test_update_user(client):
    data = {
        "username": "testuser3",
        "email": "testuser3@example.com",
        "name": "Test User 3"
    }
    create_response = client.post("/users/", json=data)
    user_id = create_response.json()["id"]

    update_data = {
        "username": "updateduser",
        "email": "testuser3@example.com",
        "name": "Updated User 3"
    }
    response = client.put(f"/users/{user_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["username"] == "updateduser"
    assert response.json()["name"] == "Updated User 3"

def test_delete_user(client):
    data = {
        "username": "testuser4",
        "email": "testuser4@example.com",
        "name": "Test User 4"
    }
    create_response = client.post("/users/", json=data)
    user_id = create_response.json()["id"]

    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204

    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "User not found"}

def test_create_duplicate_user(client):
    data = {
        "username": "duplicateuser",
        "email": "duplicate@example.com",
        "name": "Duplicate User"
    }
    client.post("/users/", json=data)

    duplicate_data = {
        "username": "anotheruser",
        "email": "duplicate@example.com",
        "name": "Another User"
    }
    response = client.post("/users/", json=duplicate_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

def test_read_user_invalid_uuid(client):
    invalid_uuid = "invalid-uuid"
    response = client.get(f"/users/{invalid_uuid}")
    assert response.status_code == 422

def test_delete_nonexistent_user(client):
    non_existent_user_id = "7c2e69fd-40e9-4bfa-b3fb-1f51fe8915b3"
    response = client.delete(f"/users/{non_existent_user_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
