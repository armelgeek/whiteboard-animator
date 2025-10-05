# Migration Guide: From Kivy App to REST API

This guide helps you understand the differences between the original Kivy application and the new REST API, and how to migrate or integrate both approaches.

## Overview

The Whiteboard Animator project now offers two ways to generate animations:

1. **Kivy GUI Application** (Original): Desktop and mobile GUI app
2. **REST API** (New): Programmatic access via HTTP API

## Key Differences

| Feature | Kivy App | REST API |
|---------|----------|----------|
| **Interface** | Graphical User Interface | HTTP REST Endpoints |
| **Use Case** | End-user desktop/mobile app | Integration with other systems |
| **Deployment** | Standalone executable | Web service |
| **Access** | Local installation | Network accessible |
| **Automation** | Manual user interaction | Programmable/scriptable |
| **Documentation** | UI tooltips | OpenAPI/Swagger docs |
| **Platform** | Android, Linux, Windows, Mac | Any platform with HTTP client |

## Architecture Comparison

### Original Kivy App Structure

```
kivy/
├── main.py              # GUI application
├── sketchApi.py         # Core logic (monolithic)
└── data/                # Resources
```

All logic is in `sketchApi.py` with direct Kivy dependencies.

### New REST API Structure

```
api/
├── app.py               # FastAPI application
├── routes/              # HTTP endpoints
│   └── animation_routes.py
├── services/            # Business logic (no HTTP)
│   ├── animation_service.py
│   └── image_service.py
├── models/              # Request/response validation
│   └── animation_models.py
└── utils/               # Helper functions
    └── image_utils.py
```

Clear separation of concerns with modular design.

## Code Comparison

### Creating Animation - Kivy App

```python
# In kivy/sketchApi.py
from kivy.clock import Clock

def initiate_sketch(
    image_path, 
    split_len, 
    frame_rate, 
    object_skip_rate, 
    bg_object_skip_rate, 
    main_img_duration, 
    callback,
    save_path=save_path,
    which_platform="linux"
):
    # Direct processing with callback
    # Uses Kivy Clock for UI updates
    ...
    Clock.schedule_once(lambda dt: callback(final_result))
```

**Pros:**
- Direct GUI integration
- Progress callbacks for UI updates
- Optimized for user interaction

**Cons:**
- Tightly coupled to Kivy
- Hard to test business logic
- Not suitable for automation
- Monolithic structure

### Creating Animation - REST API

```python
# In api/services/animation_service.py
class AnimationService:
    def create_animation(
        self,
        image_path: str,
        split_len: int = 10,
        frame_rate: int = 30,
        object_skip_rate: int = 5,
        bg_object_skip_rate: int = 8,
        main_img_duration: int = 3,
        save_path: Optional[str] = None,
        platform: str = "linux"
    ) -> Dict:
        # Framework-agnostic processing
        # Returns result dictionary
        ...
        return {
            "status": True,
            "message": "Animation created successfully",
            "video_path": final_path,
            "processing_time": processing_time
        }
```

**Pros:**
- Framework-agnostic
- Easy to test
- Suitable for automation
- Modular and maintainable
- Network accessible

**Cons:**
- No direct GUI callbacks
- Requires HTTP client for access
- Additional deployment complexity

## Migration Scenarios

### Scenario 1: Continue Using Kivy App Only

**No changes required!** The original Kivy app continues to work as before.

```bash
cd kivy/
python main.py
```

### Scenario 2: Use REST API Only

Replace Kivy app with API calls:

```python
import requests

# Instead of running GUI
response = requests.post(
    "http://localhost:8000/api/v1/animation/create",
    json={
        "image_path": "/path/to/image.png",
        "split_len": 10,
        "frame_rate": 30,
        "object_skip_rate": 5,
        "bg_object_skip_rate": 8,
        "main_img_duration": 3,
        "platform": "linux"
    }
)

result = response.json()
print(f"Video created: {result['video_path']}")
```

### Scenario 3: Hybrid Approach (Recommended)

Update Kivy app to call REST API:

**Before (in main.py):**
```python
from kivy.sketchApi import initiate_sketch

def submit_sketch_req(self):
    # Direct function call
    thread = Thread(
        target=initiate_sketch,
        args=(
            self.image_path,
            self.split_len,
            self.frame_rate,
            # ... more args
            self.task_complete_callback
        )
    )
    thread.start()
```

**After (hybrid approach):**
```python
import requests
from threading import Thread

def submit_sketch_req(self):
    def api_call():
        response = requests.post(
            "http://localhost:8000/api/v1/animation/create",
            json={
                "image_path": self.image_path,
                "split_len": self.split_len,
                "frame_rate": self.frame_rate,
                # ... more params
            }
        )
        result = response.json()
        self.task_complete_callback(result)
    
    thread = Thread(target=api_call)
    thread.start()
```

**Benefits:**
- GUI continues to work
- Can scale to multiple backend servers
- Can add caching/rate limiting at API level
- Business logic separated from UI

### Scenario 4: Web Frontend

Create a web UI that calls the API:

```javascript
// React/Vue/Angular example
async function createAnimation(imageFile) {
  // Upload image
  const formData = new FormData();
  formData.append('file', imageFile);
  
  const uploadResponse = await fetch('/upload', {
    method: 'POST',
    body: formData
  });
  
  const { path } = await uploadResponse.json();
  
  // Create animation
  const animationResponse = await fetch('/api/v1/animation/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_path: path,
      split_len: 10,
      frame_rate: 30,
      object_skip_rate: 5,
      bg_object_skip_rate: 8,
      main_img_duration: 3,
      platform: 'linux'
    })
  });
  
  const result = await animationResponse.json();
  return result.video_path;
}
```

## Integration Patterns

### Pattern 1: Direct Replacement

Replace `sketchApi.py` calls with API calls throughout your application.

**When to use:**
- Building new applications
- Want maximum flexibility
- Need network access

### Pattern 2: Adapter Pattern

Create an adapter that maintains the original interface but calls the API:

```python
# kivy/api_adapter.py
import requests
from kivy.clock import Clock

def initiate_sketch(
    image_path,
    split_len,
    frame_rate,
    object_skip_rate,
    bg_object_skip_rate,
    main_img_duration,
    callback,
    save_path=None,
    which_platform="linux"
):
    """Adapter that maintains original interface but calls API"""
    
    response = requests.post(
        "http://localhost:8000/api/v1/animation/create",
        json={
            "image_path": image_path,
            "split_len": split_len,
            "frame_rate": frame_rate,
            "object_skip_rate": object_skip_rate,
            "bg_object_skip_rate": bg_object_skip_rate,
            "main_img_duration": main_img_duration,
            "save_path": save_path,
            "platform": which_platform
        }
    )
    
    result = response.json()
    
    # Maintain callback pattern
    Clock.schedule_once(lambda dt: callback(result))
```

**Then update imports:**
```python
# Change from:
from sketchApi import initiate_sketch

# To:
from api_adapter import initiate_sketch

# Rest of code remains the same!
```

**When to use:**
- Minimal code changes
- Gradual migration
- Maintain backward compatibility

### Pattern 3: Parallel Operation

Run both implementations side by side:

```python
# Use API for some operations
api_result = call_api(image_path)

# Use original for others
local_result = initiate_sketch(image_path, ...)

# Compare or choose based on context
```

**When to use:**
- Testing/validation
- Performance comparison
- Gradual rollout

## Testing Strategy

### Testing Original Code

```python
# Hard to test - requires Kivy
from kivy.sketchApi import initiate_sketch

def test_initiate_sketch():
    # Need full Kivy environment
    # Need callback mechanism
    # Hard to isolate
    pass
```

### Testing API Code

```python
# Easy to test - no framework dependencies
from api.services.animation_service import AnimationService

def test_animation_service():
    service = AnimationService()
    result = service.create_animation(
        image_path="test.png",
        split_len=10
    )
    assert result["status"] == True
    assert "video_path" in result
```

## Performance Considerations

### Latency

| Operation | Kivy App | REST API | Notes |
|-----------|----------|----------|-------|
| Function call | ~0ms | ~1-5ms | API has network overhead |
| Image processing | Same | Same | Core logic is identical |
| Video generation | Same | Same | Same algorithms used |
| **Total overhead** | None | ~1-5ms | Negligible for long operations |

### Throughput

- **Kivy App**: Single-threaded per instance
- **REST API**: Can handle multiple concurrent requests with workers

### Resource Usage

- **Kivy App**: One process per user
- **REST API**: Shared server resources, better utilization

## Deployment Guide

### Local Development

**Kivy App:**
```bash
cd kivy/
pip install -r requirements.txt
python main.py
```

**REST API:**
```bash
cd api/
pip install -r requirements.txt
python app.py
```

### Production Deployment

**Kivy App:**
```bash
# Build executable
pyinstaller dlDesktop.spec

# Or build Android APK
buildozer android debug
```

**REST API:**
```bash
# With Gunicorn
gunicorn api.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# With Docker
docker-compose up -d
```

## Troubleshooting

### Issue: API returns 404 for image

**Cause:** API runs in different context, can't access local files

**Solution:** Use absolute paths or mount volumes in Docker

### Issue: Performance is slower with API

**Cause:** Network overhead for small operations

**Solution:** Use API for batch operations, keep original for single operations

### Issue: Can't access API from Kivy app

**Cause:** API server not running or wrong URL

**Solution:** Ensure API is running and URL is correct

```python
# Test API connectivity
import requests
try:
    response = requests.get("http://localhost:8000/api/v1/animation/health")
    print(response.json())
except Exception as e:
    print(f"API not accessible: {e}")
```

## Best Practices

### 1. Start with Adapter Pattern

Minimal changes to existing code while getting API benefits.

### 2. Use Environment Variables

```python
import os

API_URL = os.getenv("ANIMATION_API_URL", "http://localhost:8000")
USE_API = os.getenv("USE_API", "false").lower() == "true"

if USE_API:
    # Call API
else:
    # Use local implementation
```

### 3. Add Retry Logic

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_api_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    return session
```

### 4. Handle Timeouts

```python
response = requests.post(
    url,
    json=data,
    timeout=300  # 5 minutes for long operations
)
```

## Conclusion

The REST API provides a modern, maintainable architecture while keeping the original Kivy app functional. You can:

- Continue using the Kivy app as-is
- Gradually migrate to the API
- Use both in parallel
- Build new integrations on top of the API

Choose the approach that best fits your use case!
