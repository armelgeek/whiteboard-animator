# API Architecture Documentation

## Overview

The Whiteboard Animator REST API is built using a modern, layered architecture that promotes modularity, maintainability, and testability. This document provides a comprehensive overview of the API architecture and design decisions.

## Architecture Layers

### 1. Presentation Layer (Routes)

**Location:** `api/routes/`

The presentation layer handles HTTP requests and responses. It:
- Defines API endpoints using FastAPI decorators
- Validates incoming requests using Pydantic models
- Handles HTTP status codes and error responses
- Delegates business logic to the service layer

**Key Files:**
- `animation_routes.py`: Animation-related endpoints

**Responsibilities:**
- Request validation
- Response formatting
- HTTP error handling
- API documentation annotations

### 2. Service Layer

**Location:** `api/services/`

The service layer contains the core business logic. It:
- Implements animation generation algorithms
- Handles image processing operations
- Manages video encoding
- Contains no HTTP-specific code (framework-agnostic)

**Key Files:**
- `animation_service.py`: Animation generation logic
- `image_service.py`: Image analysis and preprocessing

**Responsibilities:**
- Business rule implementation
- Coordination of multiple operations
- Error handling at business logic level
- Framework-independent logic

### 3. Data Layer (Models)

**Location:** `api/models/`

The data layer defines data structures and validation rules. It:
- Uses Pydantic for request/response models
- Provides type safety and validation
- Generates OpenAPI documentation automatically

**Key Files:**
- `animation_models.py`: Request/response models

**Responsibilities:**
- Data structure definition
- Input validation
- Type enforcement
- Serialization/deserialization

### 4. Utility Layer

**Location:** `api/utils/`

The utility layer provides helper functions used across the application. It:
- Contains pure functions without side effects
- Implements reusable algorithms
- Provides mathematical and image processing utilities

**Key Files:**
- `image_utils.py`: Image processing utilities

**Responsibilities:**
- Reusable helper functions
- Mathematical operations
- Common algorithms

## Design Patterns

### 1. Separation of Concerns

Each layer has a distinct responsibility:
- **Routes**: Handle HTTP concerns
- **Services**: Implement business logic
- **Models**: Define data structures
- **Utils**: Provide helper functions

Benefits:
- Easier testing (can test business logic without HTTP)
- Better maintainability
- Clear code organization

### 2. Dependency Injection

Services are instantiated independently and injected into routes:

```python
# In routes
animation_service = AnimationService()

@router.post("/create")
async def create_animation(request: AnimationRequest):
    result = animation_service.create_animation(...)
```

Benefits:
- Easier unit testing (can mock services)
- Flexibility to swap implementations
- Loose coupling

### 3. Single Responsibility Principle

Each class/module has one primary responsibility:
- `AnimationService`: Animation generation
- `ImageService`: Image processing
- `AnimationRequest`: Request validation

Benefits:
- Easier to understand
- Easier to test
- Easier to modify

### 4. Type Safety

Comprehensive type hints throughout:

```python
def analyze_image(image_path: str) -> Dict:
    ...

class AnimationRequest(BaseModel):
    image_path: str
    split_len: int = 10
```

Benefits:
- Catch errors at development time
- Better IDE support
- Self-documenting code

## Data Flow

### Animation Creation Request Flow

```
1. Client Request
   ↓
2. FastAPI Route (animation_routes.py)
   - Validate request with Pydantic
   ↓
3. Service Layer (animation_service.py)
   - Load and preprocess image
   - Generate animation frames
   - Encode video
   ↓
4. Utility Functions (image_utils.py)
   - Image processing operations
   ↓
5. Response
   - Return video path and metadata
   ↓
6. Client receives response
```

### Image Analysis Request Flow

```
1. Client Request
   ↓
2. FastAPI Route (animation_routes.py)
   - Validate image_path parameter
   ↓
3. Image Service (image_service.py)
   - Analyze image resolution
   - Calculate common divisors
   ↓
4. Utility Functions (image_utils.py)
   - Resolution calculations
   ↓
5. Response
   - Return analysis results
   ↓
6. Client receives response
```

## Error Handling Strategy

### 1. Validation Errors (400)

Handled by Pydantic at the model level:
```python
class AnimationRequest(BaseModel):
    split_len: int = Field(10, ge=1, le=100)
```

### 2. Not Found Errors (404)

Raised when resources don't exist:
```python
if not os.path.exists(image_path):
    raise HTTPException(status_code=404, detail="Image not found")
```

### 3. Business Logic Errors (500)

Caught and wrapped in service layer:
```python
try:
    result = process_image(...)
except Exception as e:
    return {"status": False, "message": str(e)}
```

### 4. Global Error Handler

Catches all unhandled exceptions:
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"error": str(exc)})
```

## Security Considerations

### 1. Input Validation

- All inputs validated with Pydantic
- Path traversal protection needed (not implemented)
- File type validation needed (not implemented)

### 2. Resource Limits

Consider implementing:
- Request rate limiting
- File size limits
- Processing timeout limits

### 3. CORS Configuration

Currently allows all origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    ...
)
```

Production recommendation: Specify allowed origins

## Performance Considerations

### 1. Async/Await

FastAPI supports async operations:
```python
async def create_animation(request: AnimationRequest):
    # CPU-bound operations should use thread pool
    ...
```

### 2. Processing Time

Animation generation is CPU-intensive:
- Consider background task processing
- Implement job queue for large batches
- Add progress tracking

### 3. Caching

Potential caching opportunities:
- Image analysis results
- Preprocessed images
- Common divisor calculations

## Extensibility

### Adding New Endpoints

1. Create route function in appropriate routes file
2. Define request/response models
3. Implement business logic in service layer
4. Add utility functions if needed

Example:
```python
# 1. In routes/animation_routes.py
@router.post("/batch-create")
async def batch_create(requests: List[AnimationRequest]):
    ...

# 2. In models/animation_models.py
class BatchRequest(BaseModel):
    animations: List[AnimationRequest]

# 3. In services/animation_service.py
def create_batch_animations(self, requests):
    ...
```

### Adding New Services

1. Create service class in `services/`
2. Define service methods
3. Inject into routes
4. Add corresponding models

### Adding Middleware

FastAPI supports custom middleware:
```python
@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    # Pre-processing
    response = await call_next(request)
    # Post-processing
    return response
```

## Testing Strategy

### 1. Unit Tests

Test individual components in isolation:
```python
def test_find_nearest_res():
    assert find_nearest_res(700) == 720
    assert find_nearest_res(1900) == 1920
```

### 2. Integration Tests

Test API endpoints:
```python
from fastapi.testclient import TestClient

def test_analyze_endpoint():
    client = TestClient(app)
    response = client.get("/api/v1/animation/analyze?image_path=test.png")
    assert response.status_code == 200
```

### 3. Service Tests

Test business logic:
```python
def test_animation_service():
    service = AnimationService()
    result = service.create_animation(...)
    assert result["status"] == True
```

## Deployment Architecture

### Development

```
[Developer] → [FastAPI + Uvicorn (reload)]
```

### Production

```
[Users] → [Nginx/Load Balancer] → [Gunicorn + Uvicorn Workers] → [FastAPI App]
                                        ↓
                                   [File System]
```

### Docker

```
[Docker Container]
  ├── Python 3.9
  ├── FastAPI App
  ├── Dependencies (OpenCV, NumPy, etc.)
  └── Volume Mounts (input/output)
```

## Monitoring and Logging

### Logging

Structured logging at different levels:
```python
logger = logging.getLogger(__name__)
logger.info("Processing request", extra={"image_path": path})
logger.error("Processing failed", exc_info=True)
```

### Metrics to Track

- Request count by endpoint
- Response time per endpoint
- Error rate
- Active processing jobs
- Disk usage for output videos

## Future Enhancements

### 1. Authentication

Add API key or OAuth2 authentication:
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.post("/create", dependencies=[Depends(security)])
async def create_animation(...):
    ...
```

### 2. Job Queue

For long-running operations:
- Celery or RQ for task queue
- Redis for job storage
- Progress tracking endpoints

### 3. Database

Store job history and metadata:
- SQLAlchemy ORM
- PostgreSQL or SQLite
- Job status tracking

### 4. File Upload

Accept image uploads directly:
```python
from fastapi import UploadFile

@router.post("/upload-and-create")
async def upload_and_create(file: UploadFile):
    ...
```

### 5. WebSocket Progress

Real-time progress updates:
```python
from fastapi import WebSocket

@router.websocket("/ws/progress/{job_id}")
async def progress_websocket(websocket: WebSocket, job_id: str):
    ...
```

## Conclusion

The API architecture is designed to be:
- **Modular**: Clear separation of concerns
- **Maintainable**: Well-organized and documented
- **Testable**: Easy to unit test components
- **Extensible**: Easy to add new features
- **Type-Safe**: Comprehensive type hints
- **Documented**: Auto-generated OpenAPI docs

This architecture provides a solid foundation for current needs while being flexible enough to accommodate future enhancements.
