
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud
from schemas import BookOut, BookCreate, BookUpdate
import jwt
import hashlib
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT Configuration (should match main app)
SECRET_KEY = "ar-library-admin-secret-key-2024"
ALGORITHM = "HS256"

security = HTTPBearer()

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None or username != "admin":
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/books", response_model=BookOut)
def add_book(payload: BookCreate, db: Session = Depends(get_db), current_user: str = Depends(verify_admin_token)):
    return crud.create_book(db, payload)

@router.put("/books/{book_id}", response_model=BookOut)
def edit_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db), current_user: str = Depends(verify_admin_token)):
    updated = crud.update_book(db, book_id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated

@router.delete("/books/{book_id}")
def remove_book(book_id: int, db: Session = Depends(get_db), current_user: str = Depends(verify_admin_token)):
    deleted = crud.delete_book(db, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}
