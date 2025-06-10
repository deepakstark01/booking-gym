"""
Database schema definitions and SQL queries.
Contains all database-related constants and query definitions.
"""

# Table creation queries
CREATE_CLASSES_TABLE = """
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
"""

CREATE_BOOKINGS_TABLE = """
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL,
        client_name TEXT NOT NULL,
        client_email TEXT NOT NULL,
        booking_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL DEFAULT 'confirmed',
        FOREIGN KEY (class_id) REFERENCES classes (id)
    )
"""

# Index creation queries
CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_classes_datetime ON classes(datetime_utc)",
    "CREATE INDEX IF NOT EXISTS idx_bookings_email ON bookings(client_email)",
    "CREATE INDEX IF NOT EXISTS idx_bookings_class_id ON bookings(class_id)"
]

# Query definitions
class Queries:
    """SQL query constants."""
    
    # Classes queries
    GET_ALL_UPCOMING_CLASSES = """
        SELECT id, name, instructor, datetime_utc, timezone, total_slots, available_slots
        FROM classes 
        WHERE datetime(datetime_utc) > datetime('now')
        ORDER BY datetime_utc
    """
    
    GET_CLASS_BY_ID = """
        SELECT id, name, instructor, datetime_utc, timezone, total_slots, available_slots
        FROM classes 
        WHERE id = ?
    """
    
    UPDATE_CLASS_SLOTS = """
        UPDATE classes 
        SET available_slots = available_slots - 1
        WHERE id = ? AND available_slots > 0
    """
    
    # Bookings queries
    INSERT_BOOKING = """
        INSERT INTO bookings (class_id, client_name, client_email, booking_time)
        VALUES (?, ?, ?, ?)
    """
    
    GET_BOOKINGS_BY_EMAIL = """
        SELECT b.id, b.class_id, b.client_name, b.client_email, b.booking_time, b.status,
               c.name as class_name, c.instructor, c.datetime_utc, c.timezone
        FROM bookings b
        JOIN classes c ON b.class_id = c.id
        WHERE b.client_email = ?
        ORDER BY b.booking_time DESC
    """
    
    CHECK_EXISTING_BOOKING = """
        SELECT COUNT(*) as count
        FROM bookings 
        WHERE class_id = ? AND client_email = ? AND status = 'confirmed'
    """
    
    GET_CLASS_BOOKING_COUNT = """
        SELECT COUNT(*) as count
        FROM bookings 
        WHERE class_id = ? AND status = 'confirmed'
    """
