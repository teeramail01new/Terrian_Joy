#!/usr/bin/env python3
"""
Script to add sample data to the Terrain Joy database
This will populate the tables with sample data for testing the data grids
"""

import psycopg2
import sys
from datetime import datetime, date

def add_sample_data():
    """Add sample data to the database"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Check if sample data already exists
        cursor.execute("SELECT COUNT(*) FROM products")
        product_count = cursor.fetchone()[0]
        
        if product_count > 0:
            print("✓ Sample data already exists!")
            print("You can now run the main program: python main_program_terrian.py")
            return
        
        print("Adding sample data...")
        
        # Add sample categories with custom IDs
        categories_data = [
            ("CAT001", "Electronics", "Electronic devices and components"),
            ("CAT002", "Clothing", "Apparel and accessories"),
            ("CAT003", "Books", "Books and publications"),
            ("CAT004", "Tools", "Hardware tools and equipment"),
            ("CAT005", "Office Supplies", "Office and stationery items"),
        ]
        
        for cat_id, name, description in categories_data:
            cursor.execute("""
                INSERT INTO categories (id, name, description) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (cat_id, name, description))
        
        # Get category IDs
        cursor.execute("SELECT id FROM categories")
        category_ids = [row[0] for row in cursor.fetchall()]
        
        # Add sample products with custom IDs
        products_data = [
            ("PROD001", "LAPTOP001", "Dell Inspiron Laptop", category_ids[0], "pcs", 15.5, 899.99, "Active"),
            ("PROD002", "MOUSE002", "Wireless Mouse", category_ids[0], "pcs", 0.2, 25.99, "Active"),
            ("PROD003", "TSHIRT003", "Cotton T-Shirt", category_ids[1], "pcs", 0.3, 19.99, "Active"),
            ("PROD004", "BOOK004", "Python Programming", category_ids[2], "pcs", 0.8, 45.99, "Active"),
            ("PROD005", "HAMMER005", "Steel Hammer", category_ids[3], "pcs", 1.2, 29.99, "Active"),
            ("PROD006", "PEN006", "Blue Pen", category_ids[4], "pcs", 0.05, 2.99, "Active"),
            ("PROD007", "KEYBOARD007", "Mechanical Keyboard", category_ids[0], "pcs", 0.8, 89.99, "Active"),
            ("PROD008", "JEANS008", "Denim Jeans", category_ids[1], "pcs", 0.5, 59.99, "Active"),
            ("PROD009", "SCREWDRIVER009", "Phillips Screwdriver", category_ids[3], "pcs", 0.3, 12.99, "Active"),
            ("PROD010", "NOTEBOOK010", "Spiral Notebook", category_ids[4], "pcs", 0.2, 8.99, "Active"),
        ]
        
        for prod_id, sku, name, category_id, unit, weight, price, status in products_data:
            cursor.execute("""
                INSERT INTO products (id, sku, name, category_id, unit_of_measure, weight, selling_price, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (prod_id, sku, name, category_id, unit, weight, price, status == "Active"))
        
        # Add sample warehouse with custom ID
        cursor.execute("""
            INSERT INTO warehouses (id, code, name, address, contact_person, phone, email) 
            VALUES ('WH001', 'WH001', 'Main Warehouse', '123 Industrial Ave, Business District', 'John Smith', '+1-555-0123', 'warehouse@terrainjoy.com')
            ON CONFLICT (id) DO NOTHING
        """)
        
        # Get warehouse ID
        cursor.execute("SELECT id FROM warehouses WHERE code = 'WH001'")
        warehouse_id = cursor.fetchone()[0]
        
        # Get product IDs
        cursor.execute("SELECT id FROM products")
        product_ids = [row[0] for row in cursor.fetchall()]
        
        # Add sample inventory
        for i, product_id in enumerate(product_ids):
            quantity = 50 + (i * 10)  # Varying quantities
            cursor.execute("""
                INSERT INTO inventory (product_id, warehouse_id, quantity_on_hand, quantity_reserved) 
                VALUES (%s, %s, %s, %s) 
                ON CONFLICT (product_id, warehouse_id) DO UPDATE SET 
                quantity_on_hand = EXCLUDED.quantity_on_hand,
                quantity_reserved = EXCLUDED.quantity_reserved
            """, (product_id, warehouse_id, quantity, max(0, quantity - 20)))
        
        # Add sample customers with custom IDs
        customers_data = [
            ("CUST001", "CUS001", "Retail Plus Store", "Mike Johnson", "mike@retailplus.com", "+1-555-0125", "RETAIL", True),
            ("CUST002", "CUS002", "Tech Solutions Inc", "Sarah Wilson", "sarah@techsolutions.com", "+1-555-0126", "WHOLESALE", True),
            ("CUST003", "CUS003", "Office Supplies Co", "David Brown", "david@officesupplies.com", "+1-555-0127", "DISTRIBUTOR", True),
            ("CUST004", "CUS004", "Fashion Boutique", "Lisa Davis", "lisa@fashionboutique.com", "+1-555-0128", "RETAIL", True),
            ("CUST005", "CUS005", "Hardware Store", "Tom Miller", "tom@hardwarestore.com", "+1-555-0129", "WHOLESALE", True),
        ]
        
        for cust_id, code, company, contact, email, phone, cust_type, active in customers_data:
            cursor.execute("""
                INSERT INTO customers (id, customer_code, company_name, contact_person, email, phone, customer_type, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (cust_id, code, company, contact, email, phone, cust_type, active))
        
        # Add sample agents with custom IDs
        agents_data = [
            ("AGENT001", "AGT001", "Sarah", "Wilson", "sarah@terrainjoy.com", "+1-555-0130", 5.00, "North Region", "ACTIVE"),
            ("AGENT002", "AGT002", "Michael", "Chen", "michael@terrainjoy.com", "+1-555-0131", 4.50, "South Region", "ACTIVE"),
            ("AGENT003", "AGT003", "Emily", "Rodriguez", "emily@terrainjoy.com", "+1-555-0132", 6.00, "East Region", "ACTIVE"),
            ("AGENT004", "AGT004", "James", "Thompson", "james@terrainjoy.com", "+1-555-0133", 5.50, "West Region", "ACTIVE"),
        ]
        
        for agent_id, code, first_name, last_name, email, phone, commission, territory, status in agents_data:
            cursor.execute("""
                INSERT INTO agents (id, agent_code, first_name, last_name, email, phone, commission_rate, territory, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (agent_id, code, first_name, last_name, email, phone, commission, territory, status))
        
        # Get customer and agent IDs
        cursor.execute("SELECT id FROM customers")
        customer_ids = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT id FROM agents")
        agent_ids = [row[0] for row in cursor.fetchall()]
        
        # Add sample sales orders with custom IDs
        sales_orders_data = [
            ("SO001", "SO001", customer_ids[0], agent_ids[0], date(2024, 1, 15), "CONFIRMED", 1250.00),
            ("SO002", "SO002", customer_ids[1], agent_ids[1], date(2024, 1, 16), "SHIPPED", 890.00),
            ("SO003", "SO003", customer_ids[2], agent_ids[2], date(2024, 1, 17), "DELIVERED", 450.00),
            ("SO004", "SO004", customer_ids[3], agent_ids[3], date(2024, 1, 18), "PENDING", 750.00),
            ("SO005", "SO005", customer_ids[4], agent_ids[0], date(2024, 1, 19), "CONFIRMED", 1200.00),
        ]
        
        for order_id, order_num, customer_id, agent_id, order_date, status, total in sales_orders_data:
            cursor.execute("""
                INSERT INTO sales_orders (id, order_number, customer_id, agent_id, order_date, status, total_amount) 
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (order_id, order_num, customer_id, agent_id, order_date, status, total))
        
        # Add sample stock movements with custom IDs
        movements_data = [
            ("SM001", product_ids[0], warehouse_id, "IN", 100, "PURCHASE", 15.50, 1550.00),
            ("SM002", product_ids[1], warehouse_id, "IN", 50, "PURCHASE", 18.00, 900.00),
            ("SM003", product_ids[2], warehouse_id, "OUT", 25, "SALE", 15.00, 375.00),
            ("SM004", product_ids[3], warehouse_id, "IN", 75, "PURCHASE", 35.00, 2625.00),
            ("SM005", product_ids[4], warehouse_id, "TRANSFER", 30, "TRANSFER", 20.00, 600.00),
        ]
        
        for movement_id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost in movements_data:
            cursor.execute("""
                INSERT INTO stock_movements (id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (movement_id, product_id, warehouse_id, movement_type, quantity, reference_type, unit_cost, total_cost))
        
        connection.commit()
        print("✓ Sample data added successfully!")
        print("You can now run the main program: python main_program_terrian.py")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Please check your connection string and try again.")

if __name__ == "__main__":
    add_sample_data() 