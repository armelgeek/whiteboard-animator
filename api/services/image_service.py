"""
Image processing service for analysis and preprocessing
"""

import os
import cv2
import numpy as np
from typing import Dict, List, Tuple
from ..utils.image_utils import find_nearest_res, common_divisors


class ImageService:
    """Service for image analysis and preprocessing operations"""
    
    @staticmethod
    def analyze_image(image_path: str) -> Dict:
        """
        Analyze image and return resolution information and available split lengths
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary with image analysis results
            
        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image cannot be read
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        try:
            image_bgr = cv2.imread(image_path)
            if image_bgr is None:
                raise ValueError(f"Failed to read image: {image_path}")
            
            img_ht, img_wd = image_bgr.shape[0], image_bgr.shape[1]
            aspect_ratio = img_wd / img_ht
            
            # Find nearest standard resolution
            img_ht = find_nearest_res(img_ht)
            new_aspect_wd = int(img_ht * aspect_ratio)
            img_wd = find_nearest_res(new_aspect_wd)
            
            # Calculate common divisors for split lengths
            hcf_list = common_divisors(img_ht, img_wd)
            filename = os.path.basename(image_path)
            
            return {
                "image_res": f"{filename}, video resolution: {img_wd} x {img_ht}",
                "split_lens": hcf_list,
                "width": img_wd,
                "height": img_ht,
                "aspect_ratio": round(aspect_ratio, 2)
            }
        except Exception as e:
            raise ValueError(f"Error analyzing image: {str(e)}")
    
    @staticmethod
    def preprocess_image(img: np.ndarray, resize_wd: int, resize_ht: int) -> Dict:
        """
        Preprocess image for animation generation
        
        Args:
            img: Input image as numpy array
            resize_wd: Target width
            resize_ht: Target height
            
        Returns:
            Dictionary containing preprocessed image data
        """
        img_ht, img_wd = img.shape[0], img.shape[1]
        img = cv2.resize(img, (resize_wd, resize_ht))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Color histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(3, 3))
        cl1 = clahe.apply(img_gray)
        
        # Gaussian adaptive thresholding
        img_thresh = cv2.adaptiveThreshold(
            img_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 10
        )
        
        return {
            "img": img,
            "img_gray": img_gray,
            "img_thresh": img_thresh,
            "img_ht": img_ht,
            "img_wd": img_wd
        }
    
    @staticmethod
    def preprocess_hand_image(hand_path: str, hand_mask_path: str) -> Dict:
        """
        Preprocess hand image and mask for drawing
        
        Args:
            hand_path: Path to hand image
            hand_mask_path: Path to hand mask image
            
        Returns:
            Dictionary containing hand image data
        """
        hand = cv2.imread(hand_path)
        hand_mask = cv2.imread(hand_mask_path, cv2.IMREAD_GRAYSCALE)
        
        # Get extreme coordinates
        top_left, bottom_right = ImageService._get_extreme_coordinates(hand_mask)
        hand = hand[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]
        hand_mask = hand_mask[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]]
        hand_mask_inv = 255 - hand_mask
        
        # Standardize the hand masks
        hand_mask = hand_mask / 255
        hand_mask_inv = hand_mask_inv / 255
        
        # Make the hand background black
        hand_bg_ind = np.where(hand_mask == 0)
        hand[hand_bg_ind] = [0, 0, 0]
        
        hand_ht, hand_wd = hand.shape[0], hand.shape[1]
        
        return {
            "hand": hand,
            "hand_mask": hand_mask,
            "hand_mask_inv": hand_mask_inv,
            "hand_ht": hand_ht,
            "hand_wd": hand_wd
        }
    
    @staticmethod
    def _get_extreme_coordinates(mask: np.ndarray) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Get the bounding box of non-zero pixels in a mask
        
        Args:
            mask: Binary mask array
            
        Returns:
            Tuple of (top_left, bottom_right) coordinates
        """
        indices = np.where(mask == 255)
        x = indices[1]
        y = indices[0]
        
        topleft = (np.min(x), np.min(y))
        bottomright = (np.max(x), np.max(y))
        
        return topleft, bottomright
