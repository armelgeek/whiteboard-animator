"""
Data models for animation API requests and responses
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class AnimationRequest(BaseModel):
    """Request model for creating whiteboard animation"""
    
    image_path: str = Field(..., description="Path to the input image file")
    split_len: int = Field(10, ge=1, le=100, description="Grid split length for drawing")
    frame_rate: int = Field(30, ge=1, le=60, description="Output video frame rate")
    object_skip_rate: int = Field(5, ge=1, le=20, description="Skip rate for object drawing")
    bg_object_skip_rate: int = Field(8, ge=1, le=30, description="Skip rate for background drawing")
    main_img_duration: int = Field(3, ge=1, le=10, description="Duration to show final image in seconds")
    save_path: Optional[str] = Field(None, description="Custom save path for output video")
    platform: str = Field("linux", description="Target platform (linux, android, windows)")
    
    @validator("platform")
    def validate_platform(cls, v):
        allowed = ["linux", "android", "windows", "mac"]
        if v.lower() not in allowed:
            raise ValueError(f"Platform must be one of {allowed}")
        return v.lower()
    
    class Config:
        schema_extra = {
            "example": {
                "image_path": "/path/to/image.png",
                "split_len": 10,
                "frame_rate": 30,
                "object_skip_rate": 5,
                "bg_object_skip_rate": 8,
                "main_img_duration": 3,
                "platform": "linux"
            }
        }


class AnimationResponse(BaseModel):
    """Response model for animation creation"""
    
    status: bool = Field(..., description="Success status of the operation")
    message: str = Field(..., description="Status message or error description")
    video_path: Optional[str] = Field(None, description="Path to generated video file")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "status": True,
                "message": "Animation created successfully",
                "video_path": "/path/to/output/video.mp4",
                "processing_time": 45.2
            }
        }


class ImageAnalysisResponse(BaseModel):
    """Response model for image analysis"""
    
    image_res: str = Field(..., description="Image resolution information")
    split_lens: List[int] = Field(..., description="Available split length options")
    width: int = Field(..., description="Target video width")
    height: int = Field(..., description="Target video height")
    aspect_ratio: float = Field(..., description="Image aspect ratio")
    
    class Config:
        schema_extra = {
            "example": {
                "image_res": "image.png, video resolution: 1280 x 720",
                "split_lens": [1, 2, 4, 5, 8, 10, 16, 20, 40, 80],
                "width": 1280,
                "height": 720,
                "aspect_ratio": 1.78
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    
    status: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "status": False,
                "error": "ValidationError",
                "message": "Invalid image path provided",
                "details": "File does not exist"
            }
        }
