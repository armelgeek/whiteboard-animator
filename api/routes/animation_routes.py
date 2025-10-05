"""
Animation API routes
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict
import os

from ..models.animation_models import (
    AnimationRequest,
    AnimationResponse,
    ImageAnalysisResponse,
    ErrorResponse
)
from ..services.animation_service import AnimationService
from ..services.image_service import ImageService


router = APIRouter(prefix="/api/v1/animation", tags=["Animation"])

# Initialize services
animation_service = AnimationService()
image_service = ImageService()


@router.post(
    "/create",
    response_model=AnimationResponse,
    status_code=status.HTTP_200_OK,
    summary="Create whiteboard animation from image",
    description="Generate a whiteboard-style animation video from an input image",
    responses={
        200: {
            "description": "Animation created successfully",
            "model": AnimationResponse
        },
        400: {
            "description": "Invalid request",
            "model": ErrorResponse
        },
        404: {
            "description": "Image file not found",
            "model": ErrorResponse
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse
        }
    }
)
async def create_animation(request: AnimationRequest) -> AnimationResponse:
    """
    Create a whiteboard animation video from an input image.
    
    This endpoint processes an image and generates an animated video showing
    the image being drawn in a whiteboard style with a hand cursor.
    
    **Parameters:**
    - **image_path**: Path to the input image file (required)
    - **split_len**: Grid size for drawing animation (default: 10)
    - **frame_rate**: Output video frame rate (default: 30)
    - **object_skip_rate**: Drawing speed for objects (default: 5)
    - **bg_object_skip_rate**: Drawing speed for background (default: 8)
    - **main_img_duration**: Duration to show final image in seconds (default: 3)
    - **save_path**: Custom output directory (optional)
    - **platform**: Target platform: linux, android, windows, mac (default: linux)
    
    **Returns:**
    - Animation response with status, message, video path, and processing time
    """
    try:
        # Validate image file exists
        if not os.path.exists(request.image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found: {request.image_path}"
            )
        
        # Create animation
        result = animation_service.create_animation(
            image_path=request.image_path,
            split_len=request.split_len,
            frame_rate=request.frame_rate,
            object_skip_rate=request.object_skip_rate,
            bg_object_skip_rate=request.bg_object_skip_rate,
            main_img_duration=request.main_img_duration,
            save_path=request.save_path,
            platform=request.platform
        )
        
        if not result["status"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        return AnimationResponse(
            status=result["status"],
            message=result["message"],
            video_path=result.get("video_path"),
            processing_time=result.get("processing_time")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating animation: {str(e)}"
        )


@router.get(
    "/analyze",
    response_model=ImageAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze image for animation",
    description="Analyze an image and return optimal settings for animation generation",
    responses={
        200: {
            "description": "Image analyzed successfully",
            "model": ImageAnalysisResponse
        },
        400: {
            "description": "Invalid request",
            "model": ErrorResponse
        },
        404: {
            "description": "Image file not found",
            "model": ErrorResponse
        }
    }
)
async def analyze_image(image_path: str) -> ImageAnalysisResponse:
    """
    Analyze an image to determine optimal animation settings.
    
    This endpoint examines the image and returns:
    - Target video resolution
    - Available split length options (grid sizes)
    - Image dimensions and aspect ratio
    
    **Query Parameters:**
    - **image_path**: Path to the image file to analyze
    
    **Returns:**
    - Image analysis response with resolution info and split length options
    """
    try:
        # Validate image file exists
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image file not found: {image_path}"
            )
        
        # Analyze image
        result = image_service.analyze_image(image_path)
        
        return ImageAnalysisResponse(
            image_res=result["image_res"],
            split_lens=result["split_lens"],
            width=result["width"],
            height=result["height"],
            aspect_ratio=result["aspect_ratio"]
        )
        
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing image: {str(e)}"
        )


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API service is running"
)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify API is running.
    
    **Returns:**
    - Status message indicating service health
    """
    return {
        "status": "healthy",
        "service": "Whiteboard Animator API",
        "version": "1.0.0"
    }
