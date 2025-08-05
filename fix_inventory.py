#!/usr/bin/env python3
"""
Script to add inventory data with custom IDs
"""

import psycopg2

def fix_inventory():
    """Add inventory data with custom IDs"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Get product IDs
        cursor.execute("SELECT id FROM products")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(product_ids)} products")
        
        # Add inventory with custom IDs
        for i, product_id in enumerate(product_ids):
            inventory_id = f"INV{i+1:03d}"  # INV001, INV002, etc.
            quantity = 50 + (i * 10)
            
            cursor.execute("""
                INSERT INTO inventory (id, product_id, warehouse_id, quantity_on_hand, quantity_reserved) 
                VALUES (%s, %s, 'WH001', %s, %s) 
                ON CONFLICT (id) DO UPDATE SET 
                quantity_on_hand = EXCLUDED.quantity_on_hand,
                quantity_reserved = EXCLUDED.quantity_reserved
            """, (inventory_id, product_id, quantity, max(0, quantity - 20)))
            connection.commit()
            print(f"✓ Added inventory {inventory_id} for product {product_id}")
        
        print("\n✓ All inventory data added successfully!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Please check your connection string and try again.")

if __name__ == "__main__":
    fix_inventory() 