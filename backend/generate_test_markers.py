#!/usr/bin/env python3
"""
Generate ArUco markers for testing invalid marker detection
This script creates markers with IDs 3, 4, 5 which are NOT in the database
"""

import cv2
import numpy as np
import os

def generate_aruco_marker(marker_id, size=200, border_bits=1):
    """
    Generate an ArUco marker with the specified ID
    
    Args:
        marker_id (int): The ID of the marker to generate
        size (int): Size of the marker in pixels
        border_bits (int): Border size around the marker
    
    Returns:
        numpy.ndarray: The generated marker image
    """
    # Use the same dictionary as the main system (DICT_4X4_50)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    
    # Generate the marker - try different OpenCV versions
    try:
        # OpenCV 4.7+ method
        if hasattr(cv2.aruco, 'generateImageMarker'):
            marker = cv2.aruco.generateImageMarker(aruco_dict, marker_id, size, border_bits)
        else:
            # Older OpenCV method
            marker = cv2.aruco.drawMarker(aruco_dict, marker_id, size, border_bits)
    except AttributeError:
        # Fallback for very old versions
        marker = cv2.aruco.drawMarker(aruco_dict, marker_id, size)
    
    return marker

def save_marker(marker, marker_id, output_dir="markers"):
    """
    Save the marker to a file
    
    Args:
        marker (numpy.ndarray): The marker image
        marker_id (int): The marker ID
        output_dir (str): Directory to save the marker
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the marker
    filename = f"marker_{marker_id}.png"
    filepath = os.path.join(output_dir, filename)
    cv2.imwrite(filepath, marker)
    
    print(f"✅ Generated {filename} (ID: {marker_id})")
    return filepath

def main():
    """Generate test markers for invalid marker testing"""
    print("🎯 Generating ArUco markers for invalid marker testing...")
    print("These markers (IDs 3, 4, 5) are NOT in the database and should show error messages")
    print()
    
    # Marker configuration
    marker_size = 200  # pixels
    border_bits = 1    # border around marker
    
    # Generate markers with IDs 3, 4, 5 (invalid markers)
    invalid_marker_ids = [3, 4, 5]
    
    generated_files = []
    
    for marker_id in invalid_marker_ids:
        try:
            # Generate the marker
            marker = generate_aruco_marker(marker_id, marker_size, border_bits)
            
            # Save the marker
            filepath = save_marker(marker, marker_id)
            generated_files.append(filepath)
            
        except Exception as e:
            print(f"❌ Error generating marker {marker_id}: {e}")
    
    print()
    print("📁 Generated files:")
    for filepath in generated_files:
        print(f"   - {filepath}")
    
    print()
    print("🧪 Testing Instructions:")
    print("1. Print these markers or display them on another screen")
    print("2. Point your camera at them")
    print("3. You should see:")
    print("   - Red outline around the marker")
    print("   - '❌ Invalid Marker ID: X' in the AR overlay")
    print("   - Red error notification below the camera")
    print("   - Debug info showing 'X invalid' count")
    print()
    print("✅ Valid markers for comparison:")
    print("   - marker_0.png (Science Fiction)")
    print("   - marker_1.png (Computer Science)")
    print("   - marker_2.png (Literature)")

if __name__ == "__main__":
    main()
