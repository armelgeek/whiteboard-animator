"""
Example usage of the Whiteboard Animator API
"""

import requests
import json
import os

# API configuration
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    response = requests.get(f"{API_BASE_URL}/api/v1/animation/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_analyze_image(image_path):
    """Test image analysis endpoint"""
    print(f"Analyzing image: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return None
    
    response = requests.get(
        f"{API_BASE_URL}/api/v1/animation/analyze",
        params={"image_path": image_path}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def test_create_animation(image_path, **kwargs):
    """Test animation creation endpoint"""
    print(f"Creating animation for: {image_path}")
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return None
    
    # Default parameters
    payload = {
        "image_path": image_path,
        "split_len": kwargs.get("split_len", 10),
        "frame_rate": kwargs.get("frame_rate", 30),
        "object_skip_rate": kwargs.get("object_skip_rate", 5),
        "bg_object_skip_rate": kwargs.get("bg_object_skip_rate", 8),
        "main_img_duration": kwargs.get("main_img_duration", 3),
        "platform": kwargs.get("platform", "linux")
    }
    
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{API_BASE_URL}/api/v1/animation/create",
        json=payload
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    else:
        print(f"Error: {response.text}")
        return None

def main():
    """Main example function"""
    print("=" * 60)
    print("Whiteboard Animator API - Example Usage")
    print("=" * 60)
    print()
    
    # Test health check
    test_health_check()
    
    # Example image path - update this to your actual image path
    image_path = "/path/to/your/image.png"
    
    print("NOTE: Update the image_path variable to test with a real image")
    print(f"Current image_path: {image_path}")
    print()
    
    if not os.path.exists(image_path):
        print("Skipping image tests - image file not found")
        print("To test with a real image:")
        print("1. Update the image_path variable in this script")
        print("2. Ensure the API server is running: python api/app.py")
        print("3. Run this script again")
        return
    
    # Test image analysis
    analysis = test_analyze_image(image_path)
    print()
    
    if analysis:
        # Use recommended split length
        split_len = analysis["split_lens"][0] if analysis["split_lens"] else 10
        
        # Test animation creation
        result = test_create_animation(
            image_path,
            split_len=split_len,
            frame_rate=30,
            object_skip_rate=5,
            bg_object_skip_rate=8,
            main_img_duration=3,
            platform="linux"
        )
        
        if result and result.get("status"):
            print()
            print("SUCCESS!")
            print(f"Video created at: {result['video_path']}")
            print(f"Processing time: {result['processing_time']} seconds")

if __name__ == "__main__":
    main()
