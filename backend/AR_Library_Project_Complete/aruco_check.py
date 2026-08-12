import cv2
import os

# Output folder
output_folder = "markers"
os.makedirs(output_folder, exist_ok=True)

# Use predefined 4x4 dictionary with 50 unique IDs
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# Marker size in pixels
marker_size = 300

# Generate markers with IDs 0, 1, and 2
for marker_id in range(3):
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size)
    filename = os.path.join(output_folder, f"marker_{marker_id}.png")
    cv2.imwrite(filename, marker_img)
    print(f"✅ Saved marker ID {marker_id} -> {filename}")

print("✅ All markers generated!")
