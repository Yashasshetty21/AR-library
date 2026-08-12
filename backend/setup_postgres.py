import cv2
import psycopg2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ===================== PostgreSQL Connection =====================
conn = psycopg2.connect(
    dbname="ar_library",
    user="ar_user",
    password="your_password",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# ===================== Database Queries =====================
def get_shelf_name(shelf_id):
    cursor.execute("SELECT shelf_name FROM shelves WHERE marker_id = %s", (shelf_id,))
    result = cursor.fetchone()
    return result[0] if result else "Unknown Shelf"

def get_books_for_shelf(shelf_id):
    cursor.execute("""
        SELECT title, author, available
        FROM books
        WHERE marker_id = %s
    """, (shelf_id,))
    return cursor.fetchall()

# ===================== Overlay Drawing =====================
def draw_info_box(frame, marker_id, corners, shelf_name, books):
    x_min = int(min(corners[:, 0]))
    y_min = int(min(corners[:, 1]))
    x_max = int(max(corners[:, 0]))
    y_max = int(max(corners[:, 1]))

    box_width = 300
    box_height = 150 + len(books) * 25
    box_x = x_max + 10
    box_y = y_min

    overlay = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    size_factor = 1
    glow_base = Image.new("RGBA", (box_width, box_height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_base)
    glow_draw.rectangle([0, 0, box_width, box_height], fill=(0, 255, 255, 80))

    # ✅ Fix: Ensure GaussianBlur works by passing Image object, not NumPy array
    glow = glow_base.filter(ImageFilter.GaussianBlur(radius=8 * size_factor))
    overlay = Image.alpha_composite(overlay, glow)

    draw.rectangle([0, 0, box_width, box_height], outline=(0, 255, 255, 255), width=2)

    font_title = ImageFont.load_default()
    draw.text((10, 10), f"Shelf: {shelf_name}", fill=(255, 255, 255), font=font_title)

    y_text = 40
    for title, author, available in books:
        color = (0, 255, 0) if available else (255, 0, 0)
        draw.text((10, y_text), f"{title} - {author}", fill=color, font=font_title)
        y_text += 20

    frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    frame_pil.paste(overlay, (box_x, box_y), overlay)
    return cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

# ===================== ArUco Detection =====================
def detect_markers():
    cap = cv2.VideoCapture(0)
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    print("Starting AR Library (press 'q' to quit)...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

        if ids is not None:
            for i, marker_id in enumerate(ids.flatten()):
                corner_pts = corners[i].reshape((4, 2))
                shelf_name = get_shelf_name(int(marker_id))
                books = get_books_for_shelf(int(marker_id))
                frame = draw_info_box(frame, marker_id, corner_pts, shelf_name, books)

        cv2.imshow("AR Library", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# ===================== Run Script =====================
if __name__ == "__main__":
    detect_markers()
    cursor.close()
    conn.close()
