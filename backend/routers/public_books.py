
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import crud
from schemas import BookOut

router = APIRouter(tags=["Public"])

@router.get("/books", response_model=List[BookOut])
def get_books(db: Session = Depends(get_db)):
    return crud.list_books(db)

@router.get("/books/marker/{marker_id}", response_model=List[BookOut])
def get_books_by_marker(marker_id: int, db: Session = Depends(get_db)):
    return crud.list_books_by_marker(db, marker_id)
