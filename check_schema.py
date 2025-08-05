#!/usr/bin/env python3
"""
Script to check the database schema and understand field constraints
"""

import psycopg2

def check_schema():
    """Check the database schema"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Check products table structure
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'products' 
            ORDER BY ordinal_position
        """)
        
        print("\nProducts table structure:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (max length: {row[2]}, nullable: {row[3]})")
        
        # Check if there's any data
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        print(f"\nCurrent products count: {count}")
        
        # Check categories
        cursor.execute("SELECT COUNT(*) FROM categories")
        cat_count = cursor.fetchone()[0]
        print(f"Current categories count: {cat_count}")
        
        if cat_count > 0:
            cursor.execute("SELECT id, name FROM categories LIMIT 3")
            print("\nSample categories:")
            for row in cursor.fetchall():
                print(f"  ID: {row[0]} (length: {len(str(row[0]))}), Name: {row[1]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    check_schema() 