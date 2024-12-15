import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.run import app
from app.core.repo.auth.pwd_hash import PasswordHash
from app.core.repo.auth.session_tokens import SessionTokens
from app.models import User
import jwt

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"

def test_register_duplicate_user():
    # Register first user
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    # Try to register duplicate user
    response = client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    assert response.status_code == 409

def test_login_success():
    # First register a user
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    # Try to login
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password():
    # First register a user
    client.post(
        "/auth/signup",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpass123",
            "confirm_password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/auth/login",
        data={
            "username": "test@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

def test_password_hashing():
    pwd_hasher = PasswordHash()
    password = "testpass123"
    hashed = pwd_hasher.hash_password(password)
    
    # Test that hashes are different
    assert hashed != password
    
    # Test verification
    assert pwd_hasher.verify_password(password, hashed) == True
    assert pwd_hasher.verify_password("wrongpass", hashed) == False

@pytest.mark.asyncio
async def test_token_creation_and_validation():
    session_tokens = SessionTokens()
    user_id = "123"
    
    # Create token
    token_data = await session_tokens.create_access_token({"id": user_id})
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    # Decode token manually since get_current_user_id requires FastAPI dependency injection
    payload = jwt.decode(
        token_data["access_token"], 
        session_tokens.SECRET_KEY, 
        algorithms=[session_tokens.ALGORITHM]
    )
    assert payload["sub"] == user_id