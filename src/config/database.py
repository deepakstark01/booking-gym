"""
Database configuration and connection management.
Handles SQLite database setup and connection lifecycle.
"""

import sqlite3
import logging
from typing import Optional
from contextlib import contextmanager
import os

logger = logging.getLogger(__name__)

DATABASE_PATH = "db.sqlite"

def init_database() -> None:
    """Initialize the database and create tables."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            
            # Create classes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    instructor TEXT NOT NULL,
                    datetime_utc TEXT NOT NULL,
                    timezone TEXT NOT NULL DEFAULT 'Asia/Kolkata',
                    total_slots INTEGER NOT NULL,
                    available_slots INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create bookings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_id INTEGER NOT NULL,
                    client_name TEXT NOT NULL,
                    client_email TEXT NOT NULL,
                    booking_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'confirmed',
                    FOREIGN KEY (class_id) REFERENCES classes (id)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_classes_datetime ON classes(datetime_utc)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_email ON bookings(client_email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bookings_class_id ON bookings(class_id)")
            
            conn.commit()
            
            # Insert seed data if tables are empty
            cursor.execute("SELECT COUNT(*) FROM classes")
            if cursor.fetchone()[0] == 0:
                insert_seed_data(cursor)
                conn.commit()
                
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def insert_seed_data(cursor: sqlite3.Cursor) -> None:
    """Insert seed data for fitness classes."""
    from datetime import datetime, timedelta
    import pytz
    
    ist = pytz.timezone('Asia/Kolkata')
    
    # Create sample classes for the next 7 days
    base_time = datetime.now(ist).replace(hour=9, minute=0, second=0, microsecond=0)
    
    seed_classes = [
        ("Yoga", "Priya Sharma", base_time + timedelta(days=1, hours=0), 15),
        ("Zumba", "Rahul Kumar", base_time + timedelta(days=1, hours=2), 20),
        ("HIIT", "Anjali Singh", base_time + timedelta(days=1, hours=4), 12),
        ("Yoga", "Priya Sharma", base_time + timedelta(days=2, hours=0), 15),
        ("Zumba", "Rahul Kumar", base_time + timedelta(days=2, hours=2), 20),
        ("HIIT", "Anjali Singh", base_time + timedelta(days=2, hours=4), 12),
        ("Yoga", "Priya Sharma", base_time + timedelta(days=3, hours=0), 15),
        ("Zumba", "Rahul Kumar", base_time + timedelta(days=3, hours=2), 20),
        ("HIIT", "Anjali Singh", base_time + timedelta(days=3, hours=4), 12),
    ]
    
    for name, instructor, class_time, slots in seed_classes:
        # Convert to UTC for storage
        utc_time = class_time.astimezone(pytz.UTC)
        cursor.execute("""
            INSERT INTO classes (name, instructor, datetime_utc, timezone, total_slots, available_slots)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, instructor, utc_time.isoformat(), 'Asia/Kolkata', slots, slots))
    
    logger.info("Seed data inserted successfully")

@contextmanager
def get_database():
    """Get database connection context manager."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn
