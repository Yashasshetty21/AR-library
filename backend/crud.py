
from sqlalchemy.orm import Session
from models import Book
from schemas import BookCreate, BookUpdate

def list_books(db: Session):
    return db.query(Book).order_by(Book.id.desc()).all()

def list_books_by_marker(db: Session, marker_id: int):
    return db.query(Book).filter(Book.marker_id == marker_id).order_by(Book.id.asc()).all()

def create_book(db: Session, payload: BookCreate):
    obj = Book(**payload.dict())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update_book(db: Session, book_id: int, payload: BookUpdate):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return None
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(book, k, v)
    db.commit()
    db.refresh(book)
    return book

def delete_book(db: Session, book_id: int):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        return None
    db.delete(book)
    db.commit()
    return book
