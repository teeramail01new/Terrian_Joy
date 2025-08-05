#!/usr/bin/env python3
"""
Script to check inventory table structure and test inserts
"""

import psycopg2

def check_inventory():
    """Check inventory table structure"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Check inventory table structure
        print("\nInventory table structure:")
        cursor.execute("""
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'inventory' 
            ORDER BY ordinal_position
        """)
        
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} (max length: {row[2]}, nullable: {row[3]})")
        
        # Test inventory insert
        print("\nTesting inventory insert...")
        cursor.execute("SELECT id FROM products LIMIT 1")
        product_id = cursor.fetchone()[0]
        print(f"Using product ID: {product_id} (length: {len(str(product_id))})")
        
        try:
            cursor.execute("""
                INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, quantity_reserved) 
                VALUES (%s, 'WH001', 50, 10) 
                ON CONFLICT (product_id, warehouse_id) DO UPDATE SET 
                quantity_on_hand = EXCLUDED.quantity_on_hand,
                quantity_reserved = EXCLUDED.quantity_reserved
            """, (product_id,))
            connection.commit()
            print("✓ Inventory insert successful")
        except Exception as e:
            print(f"✗ Inventory insert failed: {e}")
            connection.rollback()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    check_inventory() 