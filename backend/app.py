
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import cv2
import numpy as np
import io
import base64
from PIL import Image
import psycopg2
import os
import sys
import jwt
import hashlib
from datetime import datetime, timedelta
from pydantic import BaseModel
# Add the AR library project path to Python path
ar_library_path = os.path.join(os.path.dirname(__file__), "AR_Library_Project_Complete")
sys.path.insert(0, ar_library_path)

app = FastAPI()

# JWT Configuration
SECRET_KEY = "ar-library-admin-secret-key-2024"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Pydantic models for authentication
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    success: bool
    token: str
    user: dict
    message: str = None

class UserResponse(BaseModel):
    success: bool
    user: dict
    message: str = None

# Default admin credentials (in production, store in database)
ADMIN_CREDENTIALS = {
    "admin": {
        "username": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),  # hashed password
        "role": "admin"
    }
}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        dbname='ar_library',
        user='postgres',
        password='Post',
        host='localhost',
        port='5432'
    )

# Import functions and detector config from the user's working AR system
try:
    from ar_library_postgres import (
        get_books_by_marker,
        draw_info_box,
        aruco_dict as aruco_dict_external,
        params as params_external,
    )
    print("✅ Using detector config from ar_library_postgres.py")
except ImportError as e:
    print(f"❌ Error importing AR library: {e}")
    # Fallback functions
    def get_books_by_marker(marker_id):
        return None, None
    
    def draw_info_box(frame, pos, shelf_name, books):
        return frame

# ArUco setup (prefer the user's proven configuration if available)
aruco_dict = 'aruco_dict_external' in globals() and aruco_dict_external or cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
params = 'params_external' in globals() and params_external or cv2.aruco.DetectorParameters()

# OpenCV 4.7+ moved to ArUcoDetector class. Build a detector if available.
aruco_detector = None
try:
    if hasattr(cv2.aruco, "ArucoDetector"):
        aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, params)
except Exception:
    aruco_detector = None

@app.get("/")
def read_root():
    return {"message": "AR Library API - Using Proven AR System"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "ar_system": "proven_ar_library_loaded"}

@app.post("/detect-marker")
async def detect_marker_from_image(file: UploadFile = File(...)):
    """
    Detect ArUco markers from uploaded image using the proven AR system
    """
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Use the modern API if available, otherwise fallback for older OpenCV
        if aruco_detector is not None:
            corners, ids, _ = aruco_detector.detectMarkers(image)
        else:
            corners, ids, _ = cv2.aruco.detectMarkers(image, aruco_dict, parameters=params)
        raw_marker_ids = [int(x) for x in ids.flatten()] if ids is not None else []

        results = []
        if ids is not None:
            for i, marker_id in enumerate(ids.flatten()):
                shelf, books = get_books_by_marker(int(marker_id))
                marker_corners = corners[i][0].tolist() if isinstance(corners[i], (list, tuple)) or hasattr(corners[i], 'tolist') else []
                # Always append a result so the UI can show at least the raw ID
                if shelf is not None:
                    results.append({
                        "marker_id": int(marker_id),
                        "shelf_name": shelf,
                        "corners": marker_corners,
                        "books": [
                            {"title": b[0], "author": b[1], "available": b[2]} for b in (books or [])
                        ]
                    })
                else:
                    results.append({
                        "marker_id": int(marker_id),
                        "shelf_name": "Unknown marker",
                        "corners": marker_corners,
                        "books": []
                    })
        return {
            "detected_markers": len(results),
            "results": results,
            "total_markers_found": len(raw_marker_ids),
            "raw_marker_ids": raw_marker_ids,
            "image_size": {"width": int(image.shape[1]), "height": int(image.shape[0])}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/camera-status")
def check_camera_status():
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
        if working_camera_index is None:
            return {"camera_available": False, "error": "No working camera found"}
        cap = cv2.VideoCapture(working_camera_index)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return {"camera_available": False, "error": "Cannot read from camera"}
        return {"camera_available": True, "camera_index": working_camera_index, "frame_size": f"{frame.shape[1]}x{frame.shape[0]}"}
    except Exception as e:
        return {"camera_available": False, "error": str(e)}

@app.get("/markers/{marker_id}/books")
def get_books_by_marker_id(marker_id: int):
    try:
        shelf, books = get_books_by_marker(marker_id)
        if shelf is None:
            raise HTTPException(status_code=404, detail="Marker not found")
        return {
            "marker_id": marker_id,
            "shelf_name": shelf,
            "books": [{"title": b[0], "author": b[1], "available": b[2]} for b in (books or [])]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/markers/available")
def get_available_markers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT marker_id FROM shelves ORDER BY marker_id")
        markers = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return {"available_markers": markers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/books")
def get_all_books():
    """Get all books from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.title, b.author, b.available, s.shelf_name, b.marker_id 
            FROM books b 
            LEFT JOIN shelves s ON b.marker_id = s.marker_id 
            ORDER BY b.title
        """)
        books = []
        for row in cursor.fetchall():
            books.append({
                "title": row[0],
                "author": row[1],
                "available": row[2],
                "shelf_name": row[3] or "Unknown",
                "marker_id": row[4]
            })
        cursor.close()
        conn.close()
        return {"books": books, "total": len(books)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/admin/books")
def get_admin_books():
    """Get all books for admin dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.title, b.author, b.available, s.shelf_name, b.marker_id 
            FROM books b 
            LEFT JOIN shelves s ON b.marker_id = s.marker_id 
            ORDER BY b.title
        """)
        books = []
        for row in cursor.fetchall():
            books.append({
                "id": row[0],
                "title": row[1],
                "author": row[2],
                "available": row[3],
                "shelf_name": row[4] or "Unknown",
                "marker_id": row[5]
            })
        cursor.close()
        conn.close()
        return {"books": books, "total": len(books)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/admin/books")
def add_book(
    title: str = Body(...),
    author: str = Body(...),
    marker_id: int = Body(...),
    available: bool = Body(True)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO books (title, author, marker_id, available)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (title, author, marker_id, available)
        )
        book_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True, "id": book_id}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.put("/admin/books/{book_id}")
def edit_book(
    book_id: int,
    title: str = Body(None),
    author: str = Body(None),
    marker_id: int = Body(None),
    available: bool = Body(None)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Build dynamic update query
        fields = []
        values = []
        if title is not None:
            fields.append("title=%s")
            values.append(title)
        if author is not None:
            fields.append("author=%s")
            values.append(author)
        if marker_id is not None:
            fields.append("marker_id=%s")
            values.append(marker_id)
        if available is not None:
            fields.append("available=%s")
            values.append(available)
        if not fields:
            return {"success": False, "error": "No fields to update"}
        values.append(book_id)
        query = f"UPDATE books SET {', '.join(fields)} WHERE id=%s"
        cursor.execute(query, tuple(values))
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/admin/books/{book_id}")
def delete_book(book_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/ar-system-info")
def get_ar_system_info():
    return {
        "ar_system": "Proven AR Library System",
        "aruco_dict": "DICT_4X4_50",
        "camera_detection": "Automatic camera index detection",
        "database": "PostgreSQL with shelves and books tables",
        "features": [
            "Real-time marker detection",
            "Beautiful UI overlays",
            "Database integration",
            "Font handling with fallbacks"
        ],
        "markers_available": [
            {"id": 0, "file": "marker_0.png"},
            {"id": 1, "file": "marker_1.png"},
            {"id": 2, "file": "marker_2.png"}
        ]
    }

# Authentication endpoints
@app.post("/admin/auth/login", response_model=TokenResponse)
def login_admin(login_data: LoginRequest):
    """Admin login endpoint"""
    username = login_data.username
    password = login_data.password
    
    # Check if user exists
    if username not in ADMIN_CREDENTIALS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if ADMIN_CREDENTIALS[username]["password"] != hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    
    user_info = {
        "username": username,
        "role": ADMIN_CREDENTIALS[username]["role"]
    }
    
    return TokenResponse(
        success=True,
        token=access_token,
        user=user_info,
        message="Login successful"
    )

@app.post("/admin/auth/logout")
def logout_admin():
    """Admin logout endpoint"""
    return {"success": True, "message": "Logout successful"}

@app.get("/admin/auth/verify", response_model=UserResponse)
def verify_admin_token(username: str = Depends(verify_token)):
    """Verify admin token endpoint"""
    if username in ADMIN_CREDENTIALS:
        user_info = {
            "username": username,
            "role": ADMIN_CREDENTIALS[username]["role"]
        }
        return UserResponse(
            success=True,
            user=user_info,
            message="Token valid"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
