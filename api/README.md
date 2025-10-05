# Whiteboard Animator REST API

A modern, structured REST API for generating whiteboard-style animation videos from images. This API improves modularity, performance, and maintainability of the whiteboard animator project.

## 🚀 Features

- **RESTful Architecture**: Clean, structured API with proper separation of concerns
- **Automatic Documentation**: Interactive API docs with Swagger UI and ReDoc
- **Type Safety**: Full type hints and Pydantic models for validation
- **Error Handling**: Comprehensive error handling with detailed messages
- **Multiple Platforms**: Support for Linux, Windows, Android, and Mac
- **Asynchronous**: Built on FastAPI for high performance
- **Modular Design**: Clear separation between routes, services, models, and utilities

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- OpenCV dependencies (may require system packages)

### Install Dependencies

```bash
# Navigate to the API directory
cd api

# Install Python dependencies
pip install -r requirements.txt
```

### System Dependencies (Linux)

If you encounter OpenCV issues, install system dependencies:

```bash
sudo apt-get update
sudo apt-get install -y python3-opencv libgl1-mesa-glx libglib2.0-0
```

## 🎯 Quick Start

### 1. Start the API Server

```bash
# From the api directory
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Or run directly:

```bash
python app.py
```

### 2. Access the API

- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### 3. Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/animation/health

# Analyze an image
curl "http://localhost:8000/api/v1/animation/analyze?image_path=/path/to/image.png"

# Create animation
curl -X POST "http://localhost:8000/api/v1/animation/create" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/image.png",
    "split_len": 10,
    "frame_rate": 30,
    "object_skip_rate": 5,
    "bg_object_skip_rate": 8,
    "main_img_duration": 3,
    "platform": "linux"
  }'
```

## 📡 API Endpoints

### Root Endpoint

**GET /** - API information and documentation links

```json
{
  "name": "Whiteboard Animator API",
  "version": "1.0.0",
  "documentation": {
    "interactive": "/docs",
    "redoc": "/redoc"
  }
}
```

### Health Check

**GET /api/v1/animation/health** - Check if the API is running

**Response:**
```json
{
  "status": "healthy",
  "service": "Whiteboard Animator API",
  "version": "1.0.0"
}
```

### Analyze Image

**GET /api/v1/animation/analyze** - Analyze image for optimal settings

**Query Parameters:**
- `image_path` (required): Path to the image file

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

### Create Animation

**POST /api/v1/animation/create** - Generate whiteboard animation

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
- `image_path` (required): Path to input image
- `split_len` (default: 10): Grid size for drawing (1-100)
- `frame_rate` (default: 30): Video frame rate (1-60)
- `object_skip_rate` (default: 5): Drawing speed for objects (1-20)
- `bg_object_skip_rate` (default: 8): Drawing speed for background (1-30)
- `main_img_duration` (default: 3): Final image display duration in seconds (1-10)
- `save_path` (optional): Custom output directory
- `platform` (default: "linux"): Target platform (linux, android, windows, mac)

**Response:**
```json
{
  "status": true,
  "message": "Animation created successfully",
  "video_path": "/path/to/output/video.mp4",
  "processing_time": 45.2
}
```

## 💡 Usage Examples

### Python Example

```python
import requests

# API base URL
base_url = "http://localhost:8000"

# Analyze image first
response = requests.get(
    f"{base_url}/api/v1/animation/analyze",
    params={"image_path": "/path/to/image.png"}
)
analysis = response.json()
print(f"Recommended split lengths: {analysis['split_lens']}")

# Create animation
response = requests.post(
    f"{base_url}/api/v1/animation/create",
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
if result["status"]:
    print(f"Video created: {result['video_path']}")
    print(f"Processing time: {result['processing_time']}s")
else:
    print(f"Error: {result['message']}")
```

### JavaScript Example

```javascript
// Analyze image
const analyzeResponse = await fetch(
  'http://localhost:8000/api/v1/animation/analyze?image_path=/path/to/image.png'
);
const analysis = await analyzeResponse.json();
console.log('Available split lengths:', analysis.split_lens);

// Create animation
const createResponse = await fetch(
  'http://localhost:8000/api/v1/animation/create',
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      image_path: '/path/to/image.png',
      split_len: 10,
      frame_rate: 30,
      object_skip_rate: 5,
      bg_object_skip_rate: 8,
      main_img_duration: 3,
      platform: 'linux'
    })
  }
);

const result = await createResponse.json();
if (result.status) {
  console.log('Video created:', result.video_path);
}
```

### cURL Example

```bash
# Analyze image
curl -X GET "http://localhost:8000/api/v1/animation/analyze?image_path=/path/to/image.png"

# Create animation
curl -X POST "http://localhost:8000/api/v1/animation/create" \
  -H "Content-Type: application/json" \
  -d '{
    "image_path": "/path/to/image.png",
    "split_len": 10,
    "frame_rate": 30,
    "object_skip_rate": 5,
    "bg_object_skip_rate": 8,
    "main_img_duration": 3,
    "platform": "linux"
  }'
```

## 🏗️ Architecture

### Directory Structure

```
api/
├── __init__.py              # API package initialization
├── app.py                   # FastAPI application and configuration
├── requirements.txt         # Python dependencies
├── README.md               # This file
│
├── models/                  # Data models for validation
│   ├── __init__.py
│   └── animation_models.py  # Pydantic models for requests/responses
│
├── routes/                  # API endpoints
│   ├── __init__.py
│   └── animation_routes.py  # Animation-related endpoints
│
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── animation_service.py # Animation generation logic
│   └── image_service.py     # Image processing logic
│
└── utils/                  # Utility functions
    ├── __init__.py
    └── image_utils.py      # Image processing utilities
```

### Layers

1. **Routes Layer** (`routes/`): Handles HTTP requests and responses
2. **Services Layer** (`services/`): Contains business logic
3. **Models Layer** (`models/`): Defines data structures and validation
4. **Utils Layer** (`utils/`): Provides helper functions

### Design Patterns

- **Separation of Concerns**: Clear boundaries between layers
- **Dependency Injection**: Services are injected into routes
- **Single Responsibility**: Each module has a focused purpose
- **Type Safety**: Comprehensive type hints throughout

## ⚙️ Configuration

### Environment Variables

You can configure the API using environment variables:

```bash
# API Server
export API_HOST="0.0.0.0"
export API_PORT="8000"

# Resource Paths
export HAND_IMAGE_PATH="/path/to/hand-image.png"
export OUTPUT_PATH="/path/to/output"
```

### Custom Configuration

Edit `app.py` to customize:
- CORS settings
- Logging configuration
- Rate limiting
- Authentication

## 🔨 Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

# With debug logging
uvicorn api.app:app --reload --log-level debug
```

### Testing

```bash
# Install test dependencies
pip install pytest httpx pytest-asyncio

# Run tests
pytest tests/
```

### Code Quality

```bash
# Format code
black api/

# Type checking
mypy api/

# Linting
flake8 api/
```

## 🚀 Deployment

### Production Server

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn api.app:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY api/ ./api/
COPY kivy/data/ ./kivy/data/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 📊 Performance Tips

1. **Use appropriate split_len**: Smaller values create smoother animations but take longer
2. **Adjust skip rates**: Higher skip rates = faster processing, less smooth animation
3. **Optimize image size**: Use standard resolutions for best results
4. **Enable FFmpeg**: Ensure PyAV is installed for video optimization

## 🐛 Troubleshooting

### OpenCV Import Error

```bash
# Install system dependencies
sudo apt-get install libgl1-mesa-glx libglib2.0-0
```

### PyAV/FFmpeg Issues

```bash
# Install FFmpeg
sudo apt-get install ffmpeg libavcodec-dev libavformat-dev libavutil-dev
pip install av
```

### Permission Errors

Ensure the API has write permissions to the output directory:

```bash
chmod -R 755 /path/to/output
```

## 📝 API Response Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid parameters
- **404 Not Found**: Resource not found (e.g., image file)
- **500 Internal Server Error**: Server error

## 🤝 Integration with Kivy App

The API is designed to be backward compatible with the existing Kivy application. The Kivy app can continue to use the original `sketchApi.py` or be updated to call the REST API endpoints.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with FastAPI
- Image processing with OpenCV
- Video encoding with FFmpeg/PyAV
- Original Kivy application by Whiteboard Animator Team

## 📮 Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/armelgeek/whiteboard-animator/issues
- GitHub Repository: https://github.com/armelgeek/whiteboard-animator
