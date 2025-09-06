#!/usr/bin/env python3
"""
Database initialization script
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.database.database import init_database


def main():
    """Initialize the database"""
    try:
        print("🗄️  Initializing database...")
        init_database()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()