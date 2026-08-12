
from database import Base, engine, SessionLocal
from models import Book

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # seed a few examples if empty
    if db.query(Book).count() == 0:
        samples = [
            Book(marker_id=101, title="Learning Python", author="Mark Lutz", available=True),
            Book(marker_id=101, title="Fluent Python", author="Luciano Ramalho", available=False),
            Book(marker_id=202, title="Linear Algebra Done Right", author="Sheldon Axler", available=True),
        ]
        db.add_all(samples)
        db.commit()
    db.close()
    print("DB ready.")

if __name__ == "__main__":
    main()
