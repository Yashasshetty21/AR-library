import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_CONFIG = {
    'dbname': 'ar_library',
    'user': 'postgres',
    'password': 'Post',
    'host': 'localhost',
    'port': '5432'
}

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            dbname='postgres',
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['dbname'],))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_CONFIG['dbname'])))
            print(f"Database '{DB_CONFIG['dbname']}' created successfully")
        else:
            print(f"Database '{DB_CONFIG['dbname']}' already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    
    return True

def create_tables():
    """Create the required tables for AR library"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create shelves table (matching the user's working system)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shelves (
                id SERIAL PRIMARY KEY,
                marker_id INTEGER UNIQUE NOT NULL,
                shelf_name VARCHAR(200) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create books table (matching the user's working system)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                author VARCHAR(100) NOT NULL,
                marker_id INTEGER REFERENCES shelves(marker_id),
                available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_marker_id ON books(marker_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shelves_marker_id ON shelves(marker_id)")
        
        conn.commit()
        print("Tables created successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False
    
    return True

def insert_sample_data():
    """Insert sample data for testing with the user's marker IDs"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert sample shelves (using marker IDs 0, 1, 2 from the user's markers folder)
        cursor.execute("""
            INSERT INTO shelves (marker_id, shelf_name) VALUES
            (0, 'Science Fiction'),
            (1, 'Computer Science'),
            (2, 'Literature')
            ON CONFLICT (marker_id) DO NOTHING
        """)
        
        # Insert sample books for each marker
        cursor.execute("""
            INSERT INTO books (title, author, marker_id, available) VALUES
            ('Dune', 'Frank Herbert', 0, true),
            ('The Martian', 'Andy Weir', 0, true),
            ('Foundation', 'Isaac Asimov', 0, false),
            ('Python Programming', 'John Smith', 1, true),
            ('Data Structures', 'Jane Doe', 1, true),
            ('Machine Learning', 'AI Expert', 1, false),
            ('Pride and Prejudice', 'Jane Austen', 2, true),
            ('1984', 'George Orwell', 2, true),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 2, true)
            ON CONFLICT DO NOTHING
        """)
        
        conn.commit()
        print("Sample data inserted successfully")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False
    
    return True

def main():
    print("Setting up AR Library Database...")
    print("Using proven AR system from AR_Library_Project_Complete")
    
    if create_database():
        if create_tables():
            insert_sample_data()
            print("\nAR Library database setup complete!")
            print("\nAvailable marker IDs for testing:")
            print("   - Marker 0: Science Fiction (marker_0.png)")
            print("   - Marker 1: Computer Science (marker_1.png)")
            print("   - Marker 2: Literature (marker_2.png)")
            print("\nYou can now run the AR library system!")
            print("Use the marker images from: backend/AR_Library_Project_Complete/markers/")
        else:
            print("Failed to create tables")
    else:
        print("Failed to create database")

if __name__ == "__main__":
    main()
