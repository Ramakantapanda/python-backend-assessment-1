import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.database import Base, get_db
from app.models.item_model import Item

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def setup_and_teardown():
    """Setup and teardown for each test"""
    # Setup
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown
    Base.metadata.drop_all(bind=engine)

def test_create_item(setup_and_teardown):
    """Test creating a new item"""
    response = client.post(
        "/api/v1/items",
        json={"title": "Test Item", "description": "This is a test item"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["description"] == "This is a test item"
    assert "id" in data

def test_get_item(setup_and_teardown):
    """Test getting an item by ID"""
    # First create an item
    create_response = client.post(
        "/api/v1/items",
        json={"title": "Test Item", "description": "This is a test item"}
    )
    item_id = create_response.json()["id"]
    
    # Then get the item
    response = client.get(f"/api/v1/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["description"] == "This is a test item"

def test_get_nonexistent_item(setup_and_teardown):
    """Test getting a non-existent item"""
    response = client.get("/api/v1/items/999")
    assert response.status_code == 404

def test_update_item(setup_and_teardown):
    """Test updating an item"""
    # First create an item
    create_response = client.post(
        "/api/v1/items",
        json={"title": "Test Item", "description": "This is a test item"}
    )
    item_id = create_response.json()["id"]
    
    # Then update the item
    response = client.put(
        f"/api/v1/items/{item_id}",
        json={"title": "Updated Item", "description": "This is an updated item"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Item"
    assert data["description"] == "This is an updated item"

def test_delete_item(setup_and_teardown):
    """Test deleting an item"""
    # First create an item
    create_response = client.post(
        "/api/v1/items",
        json={"title": "Test Item", "description": "This is a test item"}
    )
    item_id = create_response.json()["id"]
    
    # Then delete the item
    response = client.delete(f"/api/v1/items/{item_id}")
    assert response.status_code == 204
    
    # Verify the item is gone
    get_response = client.get(f"/api/v1/items/{item_id}")
    assert get_response.status_code == 404

def test_external_api_integration(setup_and_teardown):
    """Test external API integration"""
    # First create an item
    create_response = client.post(
        "/api/v1/items",
        json={"title": "Test Item", "description": "This is a test item"}
    )
    item_id = create_response.json()["id"]
    
    # Then call the external API endpoint
    # Note: This test might fail if external API is not available
    # In a real scenario, we would mock the external API
    response = client.get(f"/api/v1/external/fetch-data/{item_id}")
    
    # The endpoint should return 200 if external API is available
    # If external API is not available, it should return 502
    assert response.status_code in [200, 502]

def test_get_external_posts(setup_and_teardown):
    """Test getting external posts"""
    # Call the external posts endpoint
    response = client.get("/api/v1/external/posts")
    
    # The endpoint should return 200 if external API is available
    # If external API is not available, it should return 502
    assert response.status_code in [200, 502]

def test_invalid_input_validation(setup_and_teardown):
    """Test input validation"""
    # Try to create an item without required fields
    response = client.post(
        "/api/v1/items",
        json={}  # Missing required fields
    )
    assert response.status_code == 422

def test_root_endpoint(setup_and_teardown):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data