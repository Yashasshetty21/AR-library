import cv2

print("OpenCV Version:", cv2.__version__)
has_aruco = hasattr(cv2, 'aruco') and hasattr(cv2.aruco, 'drawMarker')
print("Has ArUco:", has_aruco)
