#!/usr/bin/env python3
"""
Test script to verify the AR system integration
"""

import os
import sys
import cv2
import numpy as np

# Add the AR library project path
ar_library_path = os.path.join(os.path.dirname(__file__), "AR_Library_Project_Complete")
sys.path.insert(0, ar_library_path)

def test_ar_system():
    """Test the AR system components"""
    print("🧪 Testing AR System Integration...")
    print("=" * 50)
    
    # Test 1: Check if AR library can be imported
    try:
        from ar_library_postgres import get_books_by_marker, draw_info_box
        print("✅ AR library functions imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AR library: {e}")
        return False
    
    # Test 2: Check if OpenCV and ArUco are available
    try:
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        params = cv2.aruco.DetectorParameters()
        print("✅ OpenCV ArUco detection setup successful")
    except Exception as e:
        print(f"❌ OpenCV ArUco setup failed: {e}")
        return False
    
    # Test 3: Check if camera is available
    try:
        working_camera_index = None
        for i in range(5):
            test_cap = cv2.VideoCapture(i)
            ret, frame = test_cap.read()
            if ret:
                working_camera_index = i
                test_cap.release()
                break
            test_cap.release()
        
        if working_camera_index is not None:
            print(f"✅ Camera found at index {working_camera_index}")
        else:
            print("⚠️  No camera found - this is okay for testing")
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
    
    # Test 4: Check if font files are available
    font_files = ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"]
    for font_file in font_files:
        if os.path.exists(font_file):
            print(f"✅ Font file found: {font_file}")
        else:
            print(f"⚠️  Font file missing: {font_file}")
    
    # Test 5: Check if marker images are available
    markers_path = os.path.join(ar_library_path, "markers")
    if os.path.exists(markers_path):
        marker_files = os.listdir(markers_path)
        print(f"✅ Marker images found: {len(marker_files)} files")
        for marker_file in marker_files:
            print(f"   - {marker_file}")
    else:
        print("⚠️  Markers folder not found")
    
    # Test 6: Test database connection
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname='ar_library',
            user='postgres',
            password='Post',
            host='localhost',
            port='5432'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM shelves")
        shelf_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ Database connection successful")
        print(f"   - Shelves: {shelf_count}")
        print(f"   - Books: {book_count}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Run 'python setup_ar_database.py' to set up the database")
    
    print("\n" + "=" * 50)
    print("🎉 AR System Test Complete!")
    print("\n📋 Next Steps:")
    print("1. Run 'python setup_ar_database.py' to set up the database")
    print("2. Start the backend: 'uvicorn app:app --host 0.0.0.0 --port 8000 --reload'")
    print("3. Start the frontend: 'cd frontend && npm run dev'")
    print("4. Test with your marker images!")
    
    return True

if __name__ == "__main__":
    test_ar_system()
