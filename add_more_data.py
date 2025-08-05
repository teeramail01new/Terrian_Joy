#!/usr/bin/env python3
"""
Script to add sales orders and stock movements data
"""

import psycopg2
from datetime import datetime, date

def add_more_data():
    """Add sales orders and stock movements data"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Check if sales orders already exist
        cursor.execute("SELECT COUNT(*) FROM sales_orders")
        sales_count = cursor.fetchone()[0]
        
        if sales_count > 0:
            print("✓ Sales orders already exist!")
            return
        
        print("Adding sales orders and stock movements...")
        
        # Get customer and agent IDs
        cursor.execute("SELECT id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM agents")
        agent_ids = [row[0] for row in cursor.fetchall()]
        
        # Add sample sales orders
        sales_orders_data = [
            ("SO001", "SO001", customer_ids[0], agent_ids[0], date(2024, 1, 15), "CONFIRMED", 1250.00),
            ("SO002", "SO002", customer_ids[1], agent_ids[1], date(2024, 1, 16), "SHIPPED", 890.00),
            ("SO003", "SO003", customer_ids[2], agent_ids[0], date(2024, 1, 17), "DELIVERED", 450.00),
        ]
        
        for order_id, order_num, customer_id, agent_id, order_date, status, total in sales_orders_data:
            cursor.execute("""
                INSERT INTO sales_orders (id, order_number, customer_id, agent_id, order_date, status, total_amount) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (order_id, order_num, customer_id, agent_id, order_date, status, total))
        
        # Get product IDs
        cursor.execute("SELECT id FROM products")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        # Add sample stock movements
        movements_data = [
            ("SM001", product_ids[0], "WH001", "IN", 100, "PURCHASE", 15.50, 1550.00),
            ("SM002", product_ids[1], "WH001", "IN", 50, "PURCHASE", 18.00, 900.00),
            ("SM003", product_ids[2], "WH001", "OUT", 25, "SALE", 15.00, 375.00),
            ("SM004", product_ids[3], "WH001", "IN", 75, "PURCHASE", 35.00, 2625.00),
            ("SM005", product_ids[4], "WH001", "TRANSFER", 30, "TRANSFER", 20.00, 600.00),
        ]
        
        for movement_id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost in movements_data:
            cursor.execute("""
                INSERT INTO stock_movements (id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (movement_id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost))
        
        connection.commit()
        print("✓ Sales orders and stock movements added successfully!")
        print("The data grids should now show complete data!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Please check your connection string and try again.")

if __name__ == "__main__":
    add_more_data() 