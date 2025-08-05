#!/usr/bin/env python3
"""
Script to test each field individually to identify the length issue
"""

import psycopg2

def test_field_length():
    """Test each field individually"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Test each table individually
        print("\nTesting categories...")
        try:
            cursor.execute("""
                INSERT INTO categories (id, name, description) 
                VALUES ('CAT002', 'Clothing', 'Apparel and accessories') 
                ON CONFLICT (id) DO NOTHING
            """)
            connection.commit()
            print("✓ Category CAT002 inserted")
        except Exception as e:
            print(f"✗ Category insert failed: {e}")
            connection.rollback()
        
        print("\nTesting products...")
        try:
            cursor.execute("""
                INSERT INTO products (id, sku, name, category_id, unit_of_measure, weight, selling_price, is_active) 
                VALUES ('PROD002', 'MOUSE002', 'Wireless Mouse', 'CAT001', 'pcs', 0.2, 25.99, true) 
                ON CONFLICT (id) DO NOTHING
            """)
            connection.commit()
            print("✓ Product PROD002 inserted")
        except Exception as e:
            print(f"✗ Product insert failed: {e}")
            connection.rollback()
        
        print("\nTesting customers...")
        try:
            cursor.execute("""
                INSERT INTO customers (id, customer_code, company_name, contact_person, email, phone, customer_type, is_active) 
                VALUES ('CUST001', 'CUS001', 'Retail Plus Store', 'Mike Johnson', 'mike@retailplus.com', '+1-555-0125', 'RETAIL', true) 
                ON CONFLICT (id) DO NOTHING
            """)
            connection.commit()
            print("✓ Customer CUST001 inserted")
        except Exception as e:
            print(f"✗ Customer insert failed: {e}")
            connection.rollback()
        
        print("\nTesting agents...")
        try:
            cursor.execute("""
                INSERT INTO agents (id, agent_code, first_name, last_name, email, phone, commission_rate, territory, status) 
                VALUES ('AGENT001', 'AGT001', 'Sarah', 'Wilson', 'sarah@terrainjoy.com', '+1-555-0130', 5.00, 'North Region', 'ACTIVE') 
                ON CONFLICT (id) DO NOTHING
            """)
            connection.commit()
            print("✓ Agent AGENT001 inserted")
        except Exception as e:
            print(f"✗ Agent insert failed: {e}")
            connection.rollback()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_field_length() 