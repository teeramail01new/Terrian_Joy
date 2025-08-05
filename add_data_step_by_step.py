#!/usr/bin/env python3
"""
Script to add data step by step to avoid batch processing issues
"""

import psycopg2
from datetime import datetime, date

def add_data_step_by_step():
    """Add data step by step"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Add remaining categories
        print("Adding remaining categories...")
        categories = [
            ("CAT003", "Books", "Books and publications"),
            ("CAT004", "Tools", "Hardware tools and equipment"),
            ("CAT005", "Office Supplies", "Office and stationery items"),
        ]
        
        for cat_id, name, description in categories:
            cursor.execute("""
                INSERT INTO categories (id, name, description) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (cat_id, name, description))
            connection.commit()
            print(f"✓ Added category: {name}")
        
        # Add remaining products
        print("\nAdding remaining products...")
        products = [
            ("PROD003", "TSHIRT003", "Cotton T-Shirt", "CAT002", "pcs", 0.3, 19.99, True),
            ("PROD004", "BOOK004", "Python Programming", "CAT003", "pcs", 0.8, 45.99, True),
            ("PROD005", "HAMMER005", "Steel Hammer", "CAT004", "pcs", 1.2, 29.99, True),
            ("PROD006", "PEN006", "Blue Pen", "CAT005", "pcs", 0.05, 2.99, True),
        ]
        
        for prod_id, sku, name, category_id, unit, weight, price, status in products:
            cursor.execute("""
                INSERT INTO products (id, sku, name, category_id, unit_of_measure, weight, selling_price, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (prod_id, sku, name, category_id, unit, weight, price, status))
            connection.commit()
            print(f"✓ Added product: {name}")
        
        # Add inventory
        print("\nAdding inventory...")
        cursor.execute("SELECT id FROM products")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        for i, product_id in enumerate(product_ids):
            quantity = 50 + (i * 10)
            cursor.execute("""
                INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, quantity_reserved) 
                VALUES (%s, 'WH001', %s, %s) 
                ON CONFLICT (product_id, warehouse_id) DO UPDATE SET 
                quantity_on_hand = EXCLUDED.quantity_on_hand,
                quantity_reserved = EXCLUDED.quantity_reserved
            """, (product_id, quantity, max(0, quantity - 20)))
            connection.commit()
            print(f"✓ Added inventory for product {i+1}")
        
        # Add remaining customers
        print("\nAdding remaining customers...")
        customers = [
            ("CUST002", "CUS002", "Tech Solutions Inc", "Sarah Wilson", "sarah@techsolutions.com", "+1-555-0126", "WHOLESALE", True),
            ("CUST003", "CUS003", "Office Supplies Co", "David Brown", "david@officesupplies.com", "+1-555-0127", "DISTRIBUTOR", True),
        ]
        
        for cust_id, code, company, contact, email, phone, cust_type, active in customers:
            cursor.execute("""
                INSERT INTO customers (id, customer_code, company_name, contact_person, email, phone, customer_type, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (cust_id, code, company, contact, email, phone, cust_type, active))
            connection.commit()
            print(f"✓ Added customer: {company}")
        
        # Add remaining agents
        print("\nAdding remaining agents...")
        agents = [
            ("AGENT002", "AGT002", "Michael", "Chen", "michael@terrainjoy.com", "+1-555-0131", 4.50, "South Region", "ACTIVE"),
        ]
        
        for agent_id, code, first_name, last_name, email, phone, commission, territory, status in agents:
            cursor.execute("""
                INSERT INTO agents (id, agent_code, first_name, last_name, email, phone, commission_rate, territory, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (agent_id, code, first_name, last_name, email, phone, commission, territory, status))
            connection.commit()
            print(f"✓ Added agent: {first_name} {last_name}")
        
        # Add sales orders
        print("\nAdding sales orders...")
        cursor.execute("SELECT id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM agents")
        agent_ids = [row[0] for row in cursor.fetchall()]
        
        sales_orders = [
            ("SO001", "SO001", customer_ids[0], agent_ids[0], date(2024, 1, 15), "CONFIRMED", 1250.00),
            ("SO002", "SO002", customer_ids[1], agent_ids[1], date(2024, 1, 16), "SHIPPED", 890.00),
            ("SO003", "SO003", customer_ids[2], agent_ids[0], date(2024, 1, 17), "DELIVERED", 450.00),
        ]
        
        for order_id, order_num, customer_id, agent_id, order_date, status, total in sales_orders:
            cursor.execute("""
                INSERT INTO sales_orders (id, order_number, customer_id, agent_id, order_date, status, total_amount) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (order_id, order_num, customer_id, agent_id, order_date, status, total))
            connection.commit()
            print(f"✓ Added sales order: {order_num}")
        
        # Add stock movements
        print("\nAdding stock movements...")
        movements = [
            ("SM001", product_ids[0], "WH001", "IN", 100, "PURCHASE", 15.50, 1550.00),
            ("SM002", product_ids[1], "WH001", "IN", 50, "PURCHASE", 18.00, 900.00),
            ("SM003", product_ids[2], "WH001", "OUT", 25, "SALE", 15.00, 375.00),
            ("SM004", product_ids[3], "WH001", "IN", 75, "PURCHASE", 35.00, 2625.00),
            ("SM005", product_ids[4], "WH001", "TRANSFER", 30, "TRANSFER", 20.00, 600.00),
        ]
        
        for movement_id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost in movements:
            cursor.execute("""
                INSERT INTO stock_movements (id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (movement_id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost))
            connection.commit()
            print(f"✓ Added stock movement: {movement_id}")
        
        print("\n✓ All data added successfully!")
        print("The data grids should now show complete data!")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Please check your connection string and try again.")

if __name__ == "__main__":
    add_data_step_by_step() 