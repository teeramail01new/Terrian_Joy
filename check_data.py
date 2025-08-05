#!/usr/bin/env python3
"""
Script to check what data exists in the database
"""

import psycopg2

def check_data():
    """Check what data exists in the database"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Check all tables
        tables = ['categories', 'products', 'warehouses', 'inventory', 'customers', 'agents', 'sales_orders', 'stock_movements']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 2")
                rows = cursor.fetchall()
                print(f"  Sample data: {rows[:2]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    check_data() 