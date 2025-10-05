# API Quick Reference

Quick reference for the Whiteboard Animator REST API.

## Base URL

```
http://localhost:8000
```

## Endpoints

### 🏥 Health Check

```http
GET /api/v1/animation/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Whiteboard Animator API",
  "version": "1.0.0"
}
```

### 🔍 Analyze Image

Get optimal settings for an image.

```http
GET /api/v1/animation/analyze?image_path=/path/to/image.png
```

**Query Parameters:**
- `image_path` (required): Path to image file

**Response:**
```json
{
  "image_res": "image.png, video resolution: 1280 x 720",
  "split_lens": [1, 2, 4, 5, 8, 10, 16, 20, 40, 80],
  "width": 1280,
  "height": 720,
  "aspect_ratio": 1.78
}
```

### 🎬 Create Animation

Generate whiteboard animation video.

```http
POST /api/v1/animation/create
Content-Type: application/json
```

**Request Body:**
```json
{
  "image_path": "/path/to/image.png",
  "split_len": 10,
  "frame_rate": 30,
  "object_skip_rate": 5,
  "bg_object_skip_rate": 8,
  "main_img_duration": 3,
  "save_path": null,
  "platform": "linux"
}
```

**Parameters:**
| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `image_path` | string | *required* | - | Input image path |
| `split_len` | int | 10 | 1-100 | Grid size for drawing |
| `frame_rate` | int | 30 | 1-60 | Video frame rate |
| `object_skip_rate` | int | 5 | 1-20 | Object drawing speed |
| `bg_object_skip_rate` | int | 8 | 1-30 | Background drawing speed |
| `main_img_duration` | int | 3 | 1-10 | Final image duration (seconds) |
| `save_path` | string | null | - | Custom output directory |
| `platform` | string | "linux" | linux, android, windows, mac | Target platform |

**Response:**
```json
{
  "status": true,
  "message": "Animation created successfully",
  "video_path": "/path/to/output/video.mp4",
  "processing_time": 45.2
}
```

## Quick Examples

### cURL

```bash
# Health check
curl http://localhost:8000/api/v1/animation/health

# Analyze image
curl "http://localhost:8000/api/v1/animation/analyze?image_path=/path/to/image.png"

# Create animation
curl -X POST http://localhost:8000/api/v1/animation/create \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/image.png",
    "split_len": 10,
    "frame_rate": 30
  }'
```

### Python

```python
import requests

# Analyze
response = requests.get(
    "http://localhost:8000/api/v1/animation/analyze",
    params={"image_path": "/path/to/image.png"}
)
data = response.json()

# Create
response = requests.post(
    "http://localhost:8000/api/v1/animation/create",
    json={
        "image_path": "/path/to/image.png",
        "split_len": 10,
        "frame_rate": 30
    }
)
result = response.json()
```

### JavaScript

```javascript
// Analyze
const analyzeResp = await fetch(
  'http://localhost:8000/api/v1/animation/analyze?image_path=/path/to/image.png'
);
const data = await analyzeResp.json();

// Create
const createResp = await fetch(
  'http://localhost:8000/api/v1/animation/create',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      image_path: '/path/to/image.png',
      split_len: 10,
      frame_rate: 30
    })
  }
);
const result = await createResp.json();
```

## HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Image file not found |
| 500 | Server Error | Processing error |

## Common Workflows

### Workflow 1: Quick Animation

```bash
# Single command - use defaults
curl -X POST http://localhost:8000/api/v1/animation/create \
  -H "Content-Type: application/json" \
  -d '{"image_path": "/path/to/image.png"}'
```

### Workflow 2: Optimized Animation

```bash
# Step 1: Analyze image
curl "http://localhost:8000/api/v1/animation/analyze?image_path=/path/to/image.png"

# Step 2: Use recommended split_len
curl -X POST http://localhost:8000/api/v1/animation/create \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/image.png",
    "split_len": 10,
    "frame_rate": 30
  }'
```

### Workflow 3: Batch Processing

```python
import requests

images = ["/path/to/img1.png", "/path/to/img2.png", "/path/to/img3.png"]

for image_path in images:
    response = requests.post(
        "http://localhost:8000/api/v1/animation/create",
        json={"image_path": image_path}
    )
    result = response.json()
    if result["status"]:
        print(f"✓ {image_path} -> {result['video_path']}")
    else:
        print(f"✗ {image_path}: {result['message']}")
```

## Parameter Tuning Guide

### For Faster Processing

```json
{
  "split_len": 20,          // Larger grid = faster
  "object_skip_rate": 10,   // Higher = faster
  "bg_object_skip_rate": 15,
  "frame_rate": 24          // Lower = faster
}
```

### For Better Quality

```json
{
  "split_len": 5,           // Smaller grid = smoother
  "object_skip_rate": 3,    // Lower = smoother
  "bg_object_skip_rate": 5,
  "frame_rate": 30          // Higher = smoother
}
```

### For Balanced

```json
{
  "split_len": 10,
  "object_skip_rate": 5,
  "bg_object_skip_rate": 8,
  "frame_rate": 30
}
```

## Error Handling

```python
import requests

try:
    response = requests.post(url, json=data, timeout=300)
    response.raise_for_status()  # Raise for 4xx/5xx
    result = response.json()
    
    if result.get("status"):
        print(f"Success: {result['video_path']}")
    else:
        print(f"Error: {result['message']}")
        
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.ConnectionError:
    print("Cannot connect to API")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Tips

1. **Use appropriate split_len**: Analyze image first to get recommended values
2. **Adjust skip rates**: Higher values = faster but less smooth
3. **Choose platform**: Use "android" for mobile, "linux" for servers
4. **Batch processing**: Process multiple images in parallel
5. **Timeouts**: Set appropriate timeouts for large images

## Troubleshooting

### Problem: Connection refused

**Solution:** Ensure API server is running
```bash
python api/app.py
```

### Problem: Image not found (404)

**Solution:** Use absolute paths
```python
import os
image_path = os.path.abspath("image.png")
```

### Problem: Slow processing

**Solution:** Increase skip rates and split_len
```json
{
  "split_len": 20,
  "object_skip_rate": 10
}
```

### Problem: Low quality output

**Solution:** Decrease skip rates
```json
{
  "split_len": 5,
  "object_skip_rate": 3
}
```

## Documentation Links

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Full README**: [api/README.md](README.md)
- **Architecture**: [api/ARCHITECTURE.md](ARCHITECTURE.md)
- **Migration Guide**: [api/MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)

## Support

- **Repository**: https://github.com/armelgeek/whiteboard-animator
- **Issues**: https://github.com/armelgeek/whiteboard-animator/issues
