#!/usr/bin/env python3
"""
Database Migration Script
Adds subcategory and quick_win columns to the applications table.
"""

import sqlite3
import os

# Path to database
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'avangrid.db')

def migrate_database():
    """Add new columns to applications table"""

    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(applications)")
        columns = [row[1] for row in cursor.fetchall()]

        # Add subcategory column if it doesn't exist
        if 'subcategory' not in columns:
            print("Adding subcategory column...")
            cursor.execute("ALTER TABLE applications ADD COLUMN subcategory TEXT")
            print("✓ subcategory column added")
        else:
            print("✓ subcategory column already exists")

        # Add quick_win column if it doesn't exist
        if 'quick_win' not in columns:
            print("Adding quick_win column...")
            cursor.execute("ALTER TABLE applications ADD COLUMN quick_win INTEGER DEFAULT 0")
            print("✓ quick_win column added")
        else:
            print("✓ quick_win column already exists")

        conn.commit()
        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
