import psycopg2
from datetime import datetime, date
import uuid

def add_sample_data():
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("🔄 Adding sample data to database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        # Add more customers
        customers_data = [
            ('CUST002', 'CUS002', 'Tech Solutions Inc', 'Lisa Chen', 'lisa@techsolutions.com', '+1-555-0126', 'RETAIL'),
            ('CUST003', 'CUS003', 'Office Supplies Co', 'David Brown', 'david@officesupplies.com', '+1-555-0127', 'WHOLESALE'),
            ('CUST004', 'CUS004', 'Home Decor Plus', 'Sarah Wilson', 'sarah@homedecor.com', '+1-555-0128', 'RETAIL'),
            ('CUST005', 'CUS005', 'Sports Equipment Ltd', 'Mike Davis', 'mike@sportsequipment.com', '+1-555-0129', 'WHOLESALE'),
        ]
        
        for customer in customers_data:
            cursor.execute("""
                INSERT INTO customers (id, customer_code, company_name, contact_person, email, phone, customer_type, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, customer)
        
        print(f"✅ Added {len(customers_data)} customers")
        
        # Add more agents
        agents_data = [
            ('AGENT002', 'AGT002', 'John', 'Smith', 'john@terrainjoy.com', '+1-555-0131', 'South Region', 7.5),
            ('AGENT003', 'AGT003', 'Maria', 'Garcia', 'maria@terrainjoy.com', '+1-555-0132', 'East Region', 6.0),
            ('AGENT004', 'AGT004', 'Robert', 'Johnson', 'robert@terrainjoy.com', '+1-555-0133', 'West Region', 8.0),
            ('AGENT005', 'AGT005', 'Emily', 'Davis', 'emily@terrainjoy.com', '+1-555-0134', 'Central Region', 5.5),
        ]
        
        for agent in agents_data:
            cursor.execute("""
                INSERT INTO agents (id, agent_code, first_name, last_name, email, phone, territory, commission_rate, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ACTIVE', NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, agent)
        
        print(f"✅ Added {len(agents_data)} agents")
        
        # Add more warehouses
        warehouses_data = [
            ('WH002', 'WH002', 'East Coast Warehouse', '456 Eastern Blvd', 'Mary Johnson', '+1-555-0124', 'east@terrainjoy.com'),
            ('WH003', 'WH003', 'West Coast Warehouse', '789 Western Ave', 'Tom Wilson', '+1-555-0125', 'west@terrainjoy.com'),
        ]
        
        for warehouse in warehouses_data:
            cursor.execute("""
                INSERT INTO warehouses (id, code, name, address, contact_person, phone, email, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, true, NOW())
                ON CONFLICT (id) DO NOTHING
            """, warehouse)
        
        print(f"✅ Added {len(warehouses_data)} warehouses")
        
        # Add more products
        products_data = [
            ('PROD004', 'KEYBOARD004', 'Mechanical Keyboard', 'CAT001', 'pcs', 0.8, 89.99),
            ('PROD005', 'MONITOR005', '24-inch Monitor', 'CAT001', 'pcs', 5.2, 299.99),
            ('PROD006', 'JEANS006', 'Blue Jeans', 'CAT002', 'pcs', 0.5, 49.99),
            ('PROD007', 'SHOES007', 'Running Shoes', 'CAT002', 'pcs', 0.7, 79.99),
            ('PROD008', 'BOOK008', 'Programming Guide', 'CAT003', 'pcs', 0.3, 29.99),
        ]
        
        for product in products_data:
            cursor.execute("""
                INSERT INTO products (id, sku, name, category_id, unit_of_measure, weight, selling_price, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, product)
        
        print(f"✅ Added {len(products_data)} products")
        
        # Add more inventory
        inventory_data = [
            ('INV004', 'PROD004', 'WH001', 30, 5),
            ('INV005', 'PROD005', 'WH001', 25, 8),
            ('INV006', 'PROD006', 'WH002', 40, 12),
            ('INV007', 'PROD007', 'WH002', 35, 10),
            ('INV008', 'PROD008', 'WH003', 50, 15),
        ]
        
        for inventory in inventory_data:
            cursor.execute("""
                INSERT INTO inventory (id, product_id, warehouse_id, quantity_on_hand, quantity_reserved, last_updated)
                VALUES (%s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO NOTHING
            """, inventory)
        
        print(f"✅ Added {len(inventory_data)} inventory records")
        
        # Add sales orders
        sales_orders_data = [
            ('SO001', 'SO001', 'CUST001', 'AGENT001', '2024-01-15', 'DELIVERED', 1250.00),
            ('SO002', 'SO002', 'CUST002', 'AGENT002', '2024-01-16', 'PENDING', 899.99),
            ('SO003', 'SO003', 'CUST003', 'AGENT003', '2024-01-17', 'DELIVERED', 599.99),
            ('SO004', 'SO004', 'CUST004', 'AGENT004', '2024-01-18', 'PENDING', 399.99),
        ]
        
        for order in sales_orders_data:
            cursor.execute("""
                INSERT INTO sales_orders (id, order_number, customer_id, agent_id, order_date, status, total_amount, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, order)
        
        print(f"✅ Added {len(sales_orders_data)} sales orders")
        
        # Add sales order items
        sales_items_data = [
            ('SOI001', 'SO001', 'PROD001', 1, 899.99, 0, 899.99),
            ('SOI002', 'SO001', 'PROD002', 2, 25.99, 0, 51.98),
            ('SOI003', 'SO002', 'PROD003', 3, 19.99, 0, 59.97),
            ('SOI004', 'SO003', 'PROD004', 1, 89.99, 0, 89.99),
        ]
        
        for item in sales_items_data:
            cursor.execute("""
                INSERT INTO sales_order_items (id, sales_order_id, product_id, quantity, unit_price, discount_percent, line_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, item)
        
        print(f"✅ Added {len(sales_items_data)} sales order items")
        
        # Add stock movements
        stock_movements_data = [
            ('SM001', 'PROD001', 'WH001', 'IN', 50, 'PURCHASE', 'PO001', 800.00, 40000.00),
            ('SM002', 'PROD002', 'WH001', 'IN', 100, 'PURCHASE', 'PO002', 20.00, 2000.00),
            ('SM003', 'PROD001', 'WH001', 'OUT', 1, 'SALE', 'SO001', 899.99, 899.99),
            ('SM004', 'PROD002', 'WH001', 'OUT', 2, 'SALE', 'SO001', 25.99, 51.98),
        ]
        
        for movement in stock_movements_data:
            cursor.execute("""
                INSERT INTO stock_movements (id, product_id, warehouse_id, movement_type, quantity, reference_type, reference_id, unit_cost, total_cost, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (id) DO NOTHING
            """, movement)
        
        print(f"✅ Added {len(stock_movements_data)} stock movements")
        
        # Add suppliers
        suppliers_data = [
            ('SUP001', 'SUP001', 'Tech Supplies Co', 'Alice Johnson', 'alice@techsupplies.com', '+1-555-0201', 'Net 30'),
            ('SUP002', 'SUP002', 'Fashion Wholesale', 'Bob Smith', 'bob@fashionwholesale.com', '+1-555-0202', 'Net 45'),
            ('SUP003', 'SUP003', 'Book Publishers Ltd', 'Carol Davis', 'carol@bookpublishers.com', '+1-555-0203', 'Net 30'),
        ]
        
        for supplier in suppliers_data:
            cursor.execute("""
                INSERT INTO suppliers (id, supplier_code, company_name, contact_person, email, phone, payment_terms, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, supplier)
        
        print(f"✅ Added {len(suppliers_data)} suppliers")
        
        # Add purchase orders
        purchase_orders_data = [
            ('PO001', 'PO001', 'SUP001', '2024-01-10', '2024-01-20', 'COMPLETED', 40000.00, 0, 40000.00),
            ('PO002', 'PO002', 'SUP002', '2024-01-12', '2024-01-22', 'PENDING', 2000.00, 0, 2000.00),
        ]
        
        for po in purchase_orders_data:
            cursor.execute("""
                INSERT INTO purchase_orders (id, po_number, supplier_id, order_date, expected_delivery_date, status, subtotal, tax_amount, total_amount, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, po)
        
        print(f"✅ Added {len(purchase_orders_data)} purchase orders")
        
        # Add purchase order items
        po_items_data = [
            ('POI001', 'PO001', 'PROD001', 50, 800.00, 40000.00),
            ('POI002', 'PO002', 'PROD002', 100, 20.00, 2000.00),
        ]
        
        for item in po_items_data:
            cursor.execute("""
                INSERT INTO purchase_order_items (id, purchase_order_id, product_id, quantity, unit_cost, line_total)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, item)
        
        print(f"✅ Added {len(po_items_data)} purchase order items")
        
        # Add agent commissions
        commissions_data = [
            ('COM001', 'AGENT001', 'SO001', 62.50, 5.00),
            ('COM002', 'AGENT002', 'SO002', 45.00, 5.00),
            ('COM003', 'AGENT003', 'SO003', 30.00, 5.00),
        ]
        
        for commission in commissions_data:
            cursor.execute("""
                INSERT INTO agent_commissions (id, agent_id, sales_order_id, commission_amount, commission_rate, status, payment_date, created_at)
                VALUES (%s, %s, %s, %s, %s, 'PAID', '2024-01-25', NOW())
                ON CONFLICT (id) DO NOTHING
            """, commission)
        
        print(f"✅ Added {len(commissions_data)} agent commissions")
        
        # Add users
        users_data = [
            ('USER001', 'admin', 'admin@terrainjoy.com', 'admin123', 'Admin', 'User', 'ADMIN'),
            ('USER002', 'manager', 'manager@terrainjoy.com', 'manager123', 'Manager', 'User', 'MANAGER'),
            ('USER003', 'sales', 'sales@terrainjoy.com', 'sales123', 'Sales', 'User', 'SALES'),
        ]
        
        for user in users_data:
            cursor.execute("""
                INSERT INTO users (id, username, email, password_hash, first_name, last_name, role, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW())
                ON CONFLICT (id) DO NOTHING
            """, user)
        
        print(f"✅ Added {len(users_data)} users")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n🎉 Sample data added successfully!")
        print("📊 Database now contains:")
        print("   - 5 customers")
        print("   - 5 agents") 
        print("   - 3 warehouses")
        print("   - 8 products")
        print("   - 8 inventory records")
        print("   - 4 sales orders")
        print("   - 4 sales order items")
        print("   - 4 stock movements")
        print("   - 3 suppliers")
        print("   - 2 purchase orders")
        print("   - 2 purchase order items")
        print("   - 3 agent commissions")
        print("   - 3 users")
        
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    add_sample_data() 