#!/usr/bin/env python3
"""
Simplified script to add sample data to the Terrain Joy database
"""

import psycopg2
from datetime import datetime, date

def add_simple_sample_data():
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
        
        # Add sample categories
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
        
        # Add sample products
        products_data = [
            ("PROD001", "LAPTOP001", "Dell Inspiron Laptop", "CAT001", "pcs", 15.5, 899.99, True),
            ("PROD002", "MOUSE002", "Wireless Mouse", "CAT001", "pcs", 0.2, 25.99, True),
            ("PROD003", "TSHIRT003", "Cotton T-Shirt", "CAT002", "pcs", 0.3, 19.99, True),
            ("PROD004", "BOOK004", "Python Programming", "CAT003", "pcs", 0.8, 45.99, True),
            ("PROD005", "HAMMER005", "Steel Hammer", "CAT004", "pcs", 1.2, 29.99, True),
        ]
        
        for prod_id, sku, name, category_id, unit, weight, price, status in products_data:
            cursor.execute("""
                INSERT INTO products (id, sku, name, category_id, unit_of_measure, weight, selling_price, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (prod_id, sku, name, category_id, unit, weight, price, status))
        
        # Add sample warehouse
        cursor.execute("""
            INSERT INTO warehouses (id, code, name, address, contact_person, phone, email) 
            VALUES ('WH001', 'WH001', 'Main Warehouse', '123 Industrial Ave, Business District', 'John Smith', '+1-555-0123', 'warehouse@terrainjoy.com')
            ON CONFLICT (id) DO NOTHING
        """)
        
        # Add sample inventory
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
        
        # Add sample customers
        customers_data = [
            ("CUST001", "CUS001", "Retail Plus Store", "Mike Johnson", "mike@retailplus.com", "+1-555-0125", "RETAIL", True),
            ("CUST002", "CUS002", "Tech Solutions Inc", "Sarah Wilson", "sarah@techsolutions.com", "+1-555-0126", "WHOLESALE", True),
            ("CUST003", "CUS003", "Office Supplies Co", "David Brown", "david@officesupplies.com", "+1-555-0127", "DISTRIBUTOR", True),
        ]
        
        for cust_id, code, company, contact, email, phone, cust_type, active in customers_data:
            cursor.execute("""
                INSERT INTO customers (id, customer_code, company_name, contact_person, email, phone, customer_type, is_active) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (cust_id, code, company, contact, email, phone, cust_type, active))
        
        # Add sample agents
        agents_data = [
            ("AGENT001", "AGT001", "Sarah", "Wilson", "sarah@terrainjoy.com", "+1-555-0130", 5.00, "North Region", "ACTIVE"),
            ("AGENT002", "AGT002", "Michael", "Chen", "michael@terrainjoy.com", "+1-555-0131", 4.50, "South Region", "ACTIVE"),
        ]
        
        for agent_id, code, first_name, last_name, email, phone, commission, territory, status in agents_data:
            cursor.execute("""
                INSERT INTO agents (id, agent_code, first_name, last_name, email, phone, commission_rate, territory, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                ON CONFLICT (id) DO NOTHING
            """, (agent_id, code, first_name, last_name, email, phone, commission, territory, status))
        
        connection.commit()
        print("✓ Sample data added successfully!")
        print("You can now run the main program: python main_program_terrian.py")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Please check your connection string and try again.")

if __name__ == "__main__":
    add_simple_sample_data() 