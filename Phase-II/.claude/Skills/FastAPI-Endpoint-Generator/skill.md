---
name: fastapi-endpoint-generator
description: Design and implement FastAPI endpoints with proper structure, validation, and security. Create routes with clear HTTP methods and status codes. Validate requests/responses using Pydantic models. Apply dependency injection, authentication, and authorization. Handle errors consistently with structured responses. Organize endpoints for modularity and API versioning. Use when building FastAPI applications, creating REST APIs, implementing CRUD operations, adding authentication/authorization, structuring API routes, or ensuring production-ready backend code.
---

# FastAPI Endpoint Generator

Build production-ready FastAPI endpoints with clean architecture, proper validation, security, and maintainable code.

## Core Principles

**Type Safety First**: Use Pydantic models for all requests and responses. FastAPI generates OpenAPI docs automatically.

**Explicit HTTP Semantics**: Match HTTP methods to operations (GET for reading, POST for creating, PUT/PATCH for updating, DELETE for deleting).

**Fail Fast**: Validate early with Pydantic. Return clear error messages with appropriate status codes.

**Security by Default**: Authenticate, authorize, validate inputs, sanitize outputs, rate limit endpoints.

**Dependency Injection**: Use FastAPI's dependency system for database sessions, authentication, configuration.

**Structured Responses**: Always return consistent JSON structures with clear success/error indicators.

## Project Structure

```
app/
├── main.py                   # FastAPI app initialization
├── api/
│   ├── __init__.py
│   ├── deps.py              # Shared dependencies
│   └── v1/                  # API version 1
│       ├── __init__.py
│       ├── router.py        # Version router
│       └── endpoints/
│           ├── __init__.py
│           ├── users.py
│           ├── auth.py
│           └── items.py
├── models/
│   ├── __init__.py
│   ├── user.py              # Database models (SQLAlchemy/etc)
│   └── item.py
├── schemas/
│   ├── __init__.py
│   ├── user.py              # Pydantic schemas
│   └── item.py
├── core/
│   ├── __init__.py
│   ├── config.py            # Settings
│   ├── security.py          # Auth utilities
│   └── database.py          # DB connection
└── services/
    ├── __init__.py
    ├── user.py              # Business logic
    └── item.py
```

## Basic Endpoint Structure

### Simple GET Endpoint

```python
# api/v1/endpoints/items.py
from fastapi import APIRouter, HTTPException, status
from schemas.item import Item, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/{item_id}", response_model=ItemResponse, status_code=status.HTTP_200_OK)
async def get_item(item_id: int) -> ItemResponse:
    """
    Retrieve a single item by ID.
    
    - **item_id**: The ID of the item to retrieve
    """
    item = await item_service.get_by_id(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return ItemResponse(
        success=True,
        message="Item retrieved successfully",
        data=item
    )
```

### POST Endpoint with Validation

```python
from schemas.item import ItemCreate, ItemResponse

@router.post(
    "/",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new item",
    description="Create a new item with the provided data"
)
async def create_item(item_data: ItemCreate) -> ItemResponse:
    """
    Create a new item.
    
    - **name**: Item name (required)
    - **description**: Item description (optional)
    - **price**: Item price (required, must be positive)
    """
    # Validation is automatic via Pydantic
    created_item = await item_service.create(item_data)
    
    return ItemResponse(
        success=True,
        message="Item created successfully",
        data=created_item
    )
```

### PUT/PATCH Endpoint

```python
from schemas.item import ItemUpdate

@router.patch(
    "/{item_id}",
    response_model=ItemResponse,
    status_code=status.HTTP_200_OK
)
async def update_item(
    item_id: int,
    item_data: ItemUpdate
) -> ItemResponse:
    """
    Update an existing item (partial update).
    """
    existing_item = await item_service.get_by_id(item_id)
    
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    updated_item = await item_service.update(item_id, item_data)
    
    return ItemResponse(
        success=True,
        message="Item updated successfully",
        data=updated_item
    )
```

### DELETE Endpoint

```python
@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_item(item_id: int) -> None:
    """
    Delete an item by ID.
    """
    existing_item = await item_service.get_by_id(item_id)
    
    if not existing_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    await item_service.delete(item_id)
    # 204 No Content returns empty response
```

## Pydantic Schemas

### Request Schemas

```python
# schemas/item.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    """Base schema with shared fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0, description="Item price (must be positive)")
    is_active: bool = Field(default=True)

class ItemCreate(ItemBase):
    """Schema for creating new items"""
    category_id: int = Field(..., gt=0)
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

class ItemUpdate(BaseModel):
    """Schema for updating items (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    
    class Config:
        # Ignore extra fields in request
        extra = "ignore"
```

### Response Schemas

```python
class ItemInDB(ItemBase):
    """Schema representing item in database"""
    id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode

class ItemResponse(BaseModel):
    """Standardized API response"""
    success: bool = Field(default=True)
    message: str
    data: Optional[ItemInDB] = None

class ItemListResponse(BaseModel):
    """Response for list endpoints"""
    success: bool = Field(default=True)
    message: str
    data: list[ItemInDB]
    total: int
    page: int
    page_size: int
```

### Advanced Validation

```python
from pydantic import EmailStr, HttpUrl, constr, validator

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    username: constr(min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')
    password: constr(min_length=8)
    website: Optional[HttpUrl] = None
    age: int = Field(..., ge=18, le=120)
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @field_validator('username')
    @classmethod
    def username_not_reserved(cls, v: str) -> str:
        reserved = ['admin', 'root', 'system']
        if v.lower() in reserved:
            raise ValueError('This username is reserved')
        return v
```

## Dependency Injection

### Database Session Dependency

```python
# api/deps.py
from typing import Generator
from sqlalchemy.orm import Session
from core.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides database session.
    Automatically closes session after request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in endpoint
@router.get("/items/{item_id}")
async def get_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    item = db.query(Item).filter(Item.id == item_id).first()
    return item
```

### Authentication Dependency

```python
# api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.security import verify_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Verify JWT token and return current user.
    Raises 401 if token is invalid or expired.
    """
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

# Protected endpoint
@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

### Authorization Dependency

```python
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

def require_role(required_role: UserRole):
    """
    Dependency factory for role-based authorization.
    """
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        return current_user
    
    return role_checker

# Admin-only endpoint
@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    # Only admins can delete
    await item_service.delete(item_id)
    return {"message": "Item deleted"}
```

### Custom Dependencies

```python
# Pagination dependency
class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page")
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size

@router.get("/items")
async def list_items(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    items = db.query(Item).offset(pagination.skip).limit(pagination.page_size).all()
    total = db.query(Item).count()
    
    return {
        "data": items,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size
    }
```

## Error Handling

### Custom Exception Handlers

```python
# main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

app = FastAPI()

class AppException(Exception):
    """Base exception for application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundException(AppException):
    """Raised when resource not found"""
    def __init__(self, resource: str, identifier: any):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class UnauthorizedException(AppException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "error_type": exc.__class__.__name__
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": errors
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors"""
    # Log the error (use proper logging in production)
    print(f"Unexpected error: {exc}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "error_type": "InternalServerError"
        }
    )
```

### Using Custom Exceptions

```python
@router.get("/items/{item_id}")
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    
    if not item:
        raise NotFoundException("Item", item_id)
    
    return item
```

## API Versioning

### Router Organization

```python
# api/v1/router.py
from fastapi import APIRouter
from api.v1.endpoints import users, items, auth

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])

# main.py
from fastapi import FastAPI
from api.v1.router import api_router as api_v1_router

app = FastAPI(
    title="My API",
    description="API documentation",
    version="1.0.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.include_router(api_v1_router, prefix="/api")

# URLs will be: /api/v1/items, /api/v1/users, etc.
```

### Version-Specific Models

```python
# schemas/v1/item.py
class ItemV1(BaseModel):
    name: str
    price: float

# schemas/v2/item.py
class ItemV2(BaseModel):
    name: str
    price: float
    currency: str = "USD"  # New field in v2
    tax_rate: float = 0.0
```

## Authentication & Security

### JWT Token Generation

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Generate JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token"""
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    return payload

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)
```

### Login Endpoint

```python
# api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from core.security import verify_password, create_access_token
from schemas.auth import Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
```

### CORS Configuration

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Optimization

### Background Tasks

```python
from fastapi import BackgroundTasks

def send_email_notification(email: str, message: str):
    """Send email in background"""
    # Email sending logic
    pass

@router.post("/items")
async def create_item(
    item_data: ItemCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    item = await item_service.create(item_data)
    
    # Send notification in background
    background_tasks.add_task(
        send_email_notification,
        current_user.email,
        f"Item {item.name} created successfully"
    )
    
    return item
```

### Caching

```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

@lru_cache()
def get_settings():
    """Cache settings in memory"""
    return Settings()

@router.get("/stats")
@cache(expire=60)  # Cache for 60 seconds
async def get_stats():
    """Cached endpoint"""
    stats = await compute_expensive_stats()
    return stats
```

### Database Query Optimization

```python
from sqlalchemy.orm import joinedload, selectinload

@router.get("/users/{user_id}/items")
async def get_user_items(
    user_id: int,
    db: Session = Depends(get_db)
):
    # Eager load relationships to avoid N+1 queries
    user = db.query(User).options(
        selectinload(User.items).selectinload(Item.category)
    ).filter(User.id == user_id).first()
    
    if not user:
        raise NotFoundException("User", user_id)
    
    return user.items
```

## Testing

### Test Setup

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from api.deps import get_db
from core.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

### Endpoint Tests

```python
# tests/test_items.py
def test_create_item(client, db):
    """Test creating a new item"""
    response = client.post(
        "/api/v1/items",
        json={
            "name": "Test Item",
            "description": "Test description",
            "price": 99.99,
            "category_id": 1
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Test Item"

def test_get_nonexistent_item(client, db):
    """Test getting item that doesn't exist"""
    response = client.get("/api/v1/items/999")
    
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()

def test_protected_endpoint_without_auth(client, db):
    """Test accessing protected endpoint without authentication"""
    response = client.get("/api/v1/users/profile")
    
    assert response.status_code == 401
```

## Production Checklist

Before deploying:

- [ ] All endpoints have proper status codes
- [ ] All inputs validated with Pydantic models
- [ ] Authentication and authorization implemented
- [ ] Error handling covers edge cases
- [ ] Database queries optimized (no N+1 queries)
- [ ] Proper logging configured
- [ ] CORS configured correctly
- [ ] Rate limiting implemented
- [ ] API documentation complete (auto-generated by FastAPI)
- [ ] Environment variables for secrets (never hardcode)
- [ ] Database migrations ready
- [ ] Tests written for critical endpoints
- [ ] Health check endpoint implemented

## Common Patterns

### Health Check

```python
@router.get("/health", tags=["system"])
async def health_check(db: Session = Depends(get_db)):
    """Check API and database health"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "1.0.0"
    }
```

### Bulk Operations

```python
@router.post("/items/bulk", response_model=BulkItemResponse)
async def create_items_bulk(
    items: list[ItemCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create multiple items at once"""
    if len(items) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create more than 100 items at once"
        )
    
    created_items = []
    errors = []
    
    for idx, item_data in enumerate(items):
        try:
            item = await item_service.create(item_data)
            created_items.append(item)
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})
    
    return {
        "success": len(errors) == 0,
        "created": len(created_items),
        "failed": len(errors),
        "data": created_items,
        "errors": errors
    }
```

### File Upload

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    current_user: User = Depends(get_current_user)
):
    """Upload a file"""
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: JPEG, PNG, PDF"
        )
    
    # Validate file size (10MB max)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size: 10MB"
        )
    
    # Save file
    file_path = f"uploads/{current_user.id}/{file.filename}"
    await save_file(file_path, contents)
    
    return {
        "filename": file.filename,
        "size": len(contents),
        "path": file_path
    }
```

## Configuration

```python
# core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "My API"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

## Best Practices Summary

1. **Always use type hints** - FastAPI generates docs from types
2. **Validate everything** - Use Pydantic constraints extensively
3. **Return consistent responses** - Use response models
4. **Handle errors explicitly** - Don't let exceptions bubble
5. **Use dependency injection** - Keep endpoints clean and testable
6. **Async when possible** - For I/O operations (DB, external APIs)
7. **Document endpoints** - Use docstrings and OpenAPI metadata
8. **Version your API** - Plan for changes from the start
9. **Secure by default** - Authenticate, authorize, validate
10. **Test critical paths** - Unit and integration tests
