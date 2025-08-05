#!/usr/bin/env python3
"""
Simple test script to identify which field is causing the length issue
"""

import psycopg2

def test_insert():
    """Test inserting data step by step"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Test 1: Insert a category
        print("\nTest 1: Inserting category...")
        try:
            cursor.execute("""
                INSERT INTO categories (id, name, description) 
                VALUES ('CAT001', 'Electronics', 'Electronic devices and components') 
                ON CONFLICT (id) DO NOTHING
            """)
            connection.commit()
            print("✓ Category inserted successfully")
        except Exception as e:
            print(f"✗ Category insert failed: {e}")
            connection.rollback()
        
        # Test 2: Insert a product
        print("\nTest 2: Inserting product...")
        try:
            cursor.execute("""
                INSERT INTO products (id, sku, name, category_id, unit_of_measure, weight, selling_price, is_active) 
                VALUES ('PROD001', 'LAPTOP001', 'Dell Inspiron Laptop', 'CAT001', 'pcs', 15.5, 899.99, true) 
                ON CONFLICT (id) DO NOTHING
            """)
            connection.commit()
            print("✓ Product inserted successfully")
        except Exception as e:
            print(f"✗ Product insert failed: {e}")
            connection.rollback()
        
        # Test 3: Insert a warehouse
        print("\nTest 3: Inserting warehouse...")
        try:
            cursor.execute("""
                INSERT INTO warehouses (id, code, name, address, contact_person, phone, email) 
                VALUES ('WH001', 'WH001', 'Main Warehouse', '123 Industrial Ave', 'John Smith', '+1-555-0123', 'warehouse@terrainjoy.com') 
                ON CONFLICT (id) DO NOTHING
            """)
            connection.commit()
            print("✓ Warehouse inserted successfully")
        except Exception as e:
            print(f"✗ Warehouse insert failed: {e}")
            connection.rollback()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_insert() 