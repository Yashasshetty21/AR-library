
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
from database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    marker_id = Column(Integer, index=True, nullable=True)  # allows multiple books per marker
    title = Column(String(200), nullable=False)
    author = Column(String(100), nullable=False)
    available = Column(Boolean, default=True, nullable=False)
