import cv2
import psycopg2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import time

# PostgreSQL connection configuration
DB_CONFIG = {
    'dbname': 'ar_library',
    'user': 'postgres',
    'password': 'Post',
    'host': 'localhost',
    'port': '5432'
}

# Fetch shelf name and books
def get_books_by_marker(marker_id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT shelf_name FROM shelves WHERE marker_id = %s", 
            (marker_id,)
        )
        shelf_result = cursor.fetchone()

        if shelf_result:
            shelf = shelf_result[0]

            # Explicitly choose the correct column: `available`
            cursor.execute(
                "SELECT title, author, available FROM books WHERE marker_id = %s", 
                (marker_id,)
            )
            books_result = cursor.fetchall()

            books = [
                (
                    row[0],  # title
                    row[1],  # author
                    bool(row[2]) if row[2] is not None else False
                )
                for row in books_result
            ]

            cursor.close()
            conn.close()
            return shelf, books

        cursor.close()
        conn.close()
        return None, None
        
    except Exception as e:
        print(f"Database error in get_books_by_marker: {e}")
        return None, None



# Draw futuristic glowing info box with animation and text safety
def draw_info_box(frame, pos, shelf_name, books):
    img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
    frame_w, frame_h = img_pil.size

    # Fonts
    def try_fonts(candidates, size):
        for path in candidates:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
        return None

    font_title = try_fonts(["arial.ttf", "DejaVuSans-Bold.ttf", "dejavu-sans/DejaVuSans-Bold.ttf"], 34)
    font_books = try_fonts(["arial.ttf", "DejaVuSans.ttf", "dejavu-sans/DejaVuSans.ttf"], 26)
    font_books_small = try_fonts(["arial.ttf", "DejaVuSans.ttf", "dejavu-sans/DejaVuSans.ttf"], 22)
    font_emoji = try_fonts(["seguiemj.ttf", "Segoe UI Emoji.ttf"], 28)

    if font_title is None:
        font_title = ImageFont.load_default()
    if font_books is None:
        font_books = ImageFont.load_default()
    if font_books_small is None:
        font_books_small = ImageFont.load_default()
    if font_emoji is None:
        font_emoji = ImageFont.load_default()

    # Helpers
    def text_width(text, font):
        try:
            bbox = font.getbbox(text)
            return bbox[2] - bbox[0]
        except Exception:
            bbox = ImageDraw.Draw(Image.new("RGBA", (1,1))).textbbox((0,0), text, font=font)
            return bbox[2] - bbox[0]

    def truncate_text(text, font, max_width):
        if text_width(text, font) <= max_width:
            return text
        ellipsis = "…"
        max_text = text
        while max_text and text_width(max_text + ellipsis, font) > max_width:
            max_text = max_text[:-1]
        return (max_text + ellipsis) if max_text else ellipsis

    def wrap_text_two_lines(text, font, max_width):
        words = text.split()
        if not words:
            return [""]
        lines = ["", ""]
        # build first line
        for idx, w in enumerate(words):
            test = (lines[0] + (" " if lines[0] else "") + w)
            if text_width(test, font) <= max_width:
                lines[0] = test
            else:
                # rest goes to second line
                remaining = words[idx:]
                second = ""
                for ww in remaining:
                    test2 = (second + (" " if second else "") + ww)
                    if text_width(test2, font) <= max_width:
                        second = test2
                    else:
                        break
                lines[1] = truncate_text(second, font, max_width)
                return [lines[0], lines[1]]
        return [lines[0]]

    # Layout metrics
    padding = 16
    emoji_offset_x = 56  # reserved icon column width
    title_line_h = 34 + 8
    book_title_h = 26 + 10
    author_line_h = 22 + 10
    base_width = min(560, frame_w - 2 * padding)

    # Start with given position, then clamp after sizing
    x, y = int(pos[0]), int(pos[1])

    # Compute text layout inside a box overlay (local coords)
    content_x = padding
    content_y = padding
    max_text_width = max(40, base_width - 2 * padding - emoji_offset_x)

    # Measure title (wrap up to 2 lines)
    raw_title = str(shelf_name) if shelf_name not in (None, "") else "Shelf"
    shelf_text = f"Shelf: {raw_title}"
    title_lines = wrap_text_two_lines(shelf_text, font_title, base_width - 2 * padding)
    box_height = padding + len(title_lines) * title_line_h + 8

    # Each book uses two lines (title + author); if none, reserve one line for placeholder
    if books:
        for (title, author, available) in books:
            box_height += book_title_h + author_line_h
    else:
        box_height += author_line_h

    box_height += padding
    box_width = base_width

    # Clamp box to frame
    margin = 10
    if x + box_width + margin > frame_w:
        x = max(margin, frame_w - box_width - margin)
    else:
        x = max(margin, x)
    if y + box_height + margin > frame_h:
        y = max(margin, frame_h - box_height - margin)
    else:
        y = max(margin, y)

    # Create box-sized overlay
    box_img = Image.new("RGBA", (box_width, box_height), (0,0,0,0))
    box_draw = ImageDraw.Draw(box_img)

    # Animated glow
    t = time.time()
    pulse = 0.5 + 0.5 * math.sin(t * 2.0)
    glow_alpha = int(70 + 80 * pulse)
    border_alpha = int(150 + 80 * pulse)
    glow_radius = int(6 + 6 * pulse)

    # Background panel
    box_draw.rounded_rectangle(
        [0, 0, box_width, box_height],
        radius=18,
        fill=(10, 20, 40, 200),
        outline=(0, 255, 255, border_alpha),
        width=2
    )

    # Glow layer
    glow_layer = Image.new("RGBA", (box_width, box_height), (0,0,0,0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.rounded_rectangle(
        [0, 0, box_width, box_height],
        radius=18,
        fill=(0, 255, 255, glow_alpha)
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=glow_radius))
    box_img = Image.alpha_composite(glow_layer, box_img)

    # IMPORTANT: Recreate draw context after compositing
    box_draw = ImageDraw.Draw(box_img)

    # Title lines
    ty = content_y
    for line in title_lines:
        box_draw.text((content_x, ty), line, font=font_title, fill=(0, 255, 255, 255))
        ty += title_line_h
    ty += 2

    # Book list (two lines per entry)
    if not books:
        placeholder = "No books found"
        box_draw.text((content_x, ty), placeholder, font=font_books_small, fill=(200, 200, 200, 255))
        ty += author_line_h
    else:
        for (title, author, available) in books:
            status_glyph = "✅" if available else "❌"
            status_color = (0, 255, 0, 255) if available else (255, 0, 0, 255)

            # Colored emoji icon centered in the icon column
            emoji_size = getattr(font_emoji, "size", 28)
            emoji_x = content_x + max(0, (emoji_offset_x - emoji_size) // 2)
            emoji_y = ty + max(0, (book_title_h - emoji_size) // 2) - 2
            box_draw.text((emoji_x, emoji_y), status_glyph, font=font_emoji, fill=status_color)

            # Title (truncate to fit)
            safe_title = truncate_text(str(title), font_books, max_text_width)
            box_draw.text((content_x + emoji_offset_x, ty), safe_title, font=font_books, fill=(255, 255, 255, 255))
            ty += book_title_h

            # Author line
            safe_author = truncate_text("by " + str(author), font_books_small, max_text_width)
            box_draw.text((content_x + emoji_offset_x, ty), safe_author, font=font_books_small, fill=(180, 180, 180, 255))
            ty += author_line_h

    # Paste into frame
    img_pil.paste(box_img, (x, y), box_img)
    frame[:] = cv2.cvtColor(np.array(img_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    return frame

# ArUco setup
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
params = cv2.aruco.DetectorParameters_create()

if __name__ == "__main__":
    # Detect working camera
    working_camera_index = None
    for i in range(5):
        test_cap = cv2.VideoCapture(i)
        ret, frame = test_cap.read()
        if ret:
            working_camera_index = i
            test_cap.release()
            break
        test_cap.release()

    if working_camera_index is None:
        print("No working camera found.")
        exit()

    cap = cv2.VideoCapture(working_camera_index)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=params)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            for i, marker_id in enumerate(ids.flatten()):
                shelf, books = get_books_by_marker(int(marker_id))
                pos = tuple(corners[i][0][0].astype(int))
                if shelf is not None:
                    draw_info_box(frame, pos, shelf, books or [])
                else:
                    cv2.putText(frame, f"Unknown marker ID: {marker_id}", pos,
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        cv2.imshow("AR Library", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()  