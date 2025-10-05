"""
Utility functions for image processing
"""

import numpy as np
from typing import List


def find_nearest_res(given: int) -> int:
    """
    Find the nearest standard resolution value
    
    Args:
        given: Input resolution value
        
    Returns:
        Nearest standard resolution
    """
    arr = np.array([640, 360, 480, 1280, 720, 1920, 1080, 2560, 1440, 3840, 2160, 7680, 4320])
    idx = (np.abs(arr - given)).argmin()
    return int(arr[idx])


def common_divisors(num1: int, num2: int) -> List[int]:
    """
    Find all common divisors of two numbers
    
    Args:
        num1: First number
        num2: Second number
        
    Returns:
        Sorted list of common divisors
    """
    divisors1 = []
    divisors2 = []
    common_divs = []
    
    # Find divisors of num1
    for i in range(1, num1 + 1):
        if num1 % i == 0:
            divisors1.append(i)
    
    # Find divisors of num2
    for i in range(1, num2 + 1):
        if num2 % i == 0:
            divisors2.append(i)
    
    # Find common divisors
    for divisor in divisors1:
        if divisor in divisors2:
            common_divs.append(divisor)
    
    common_divs.sort()
    return common_divs


def euc_dist(arr1: np.ndarray, point: np.ndarray) -> np.ndarray:
    """
    Calculate Euclidean distance between array of points and a single point
    
    Args:
        arr1: Array of points
        point: Single point
        
    Returns:
        Array of distances
    """
    square_sub = (arr1 - point) ** 2
    return np.sqrt(np.sum(square_sub, axis=1))
