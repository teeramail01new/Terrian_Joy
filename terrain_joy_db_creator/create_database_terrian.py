import flet as ft
import psycopg2
import threading
import time

class DatabaseCreator:
    def __init__(self):
        self.connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
        self.connection = None
        self.page = None
        
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Terrain Joy Database Creator"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 800
        page.window_height = 600
        page.scroll = ft.ScrollMode.AUTO
        
        # Connection status
        self.connection_status = ft.Text("Not connected", color=ft.colors.RED)
        
        # Progress bar
        self.progress_bar = ft.ProgressBar(width=400, visible=False)
        self.progress_text = ft.Text("", visible=False)
        
        # Logs
        self.log_container = ft.Container(
            content=ft.Column([], scroll=ft.ScrollMode.AUTO),
            height=300,
            width=750,
            border=ft.border.all(1, ft.colors.GREY_400),
            padding=10,
            bgcolor=ft.colors.GREY_100
        )
        
        # Buttons
        self.connect_btn = ft.ElevatedButton(
            "Connect to Database",
            on_click=self.connect_to_database,
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE
        )
        
        self.create_tables_btn = ft.ElevatedButton(
            "Create All Tables",
            on_click=self.create_all_tables,
            disabled=True,
            color=ft.colors.WHITE,
            bgcolor=ft.colors.GREEN
        )
        
        self.clear_logs_btn = ft.ElevatedButton(
            "Clear Logs",
            on_click=self.clear_logs,
            color=ft.colors.WHITE,
            bgcolor=ft.colors.ORANGE
        )
        
        # Layout
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Terrain Joy Database Setup", size=30, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    
                    # Connection section
                    ft.Row([
                        ft.Text("Connection Status:", weight=ft.FontWeight.BOLD),
                        self.connection_status
                    ]),
                    
                    ft.Row([
                        self.connect_btn,
                        self.create_tables_btn,
                        self.clear_logs_btn
                    ]),
                    
                    # Progress section
                    self.progress_bar,
                    self.progress_text,
                    
                    ft.Divider(),
                    
                    # Logs section
                    ft.Text("Database Creation Logs:", weight=ft.FontWeight.BOLD),
                    self.log_container
                ]),
                padding=20
            )
        )
    
    def log_message(self, message, color=ft.colors.BLACK):
        """Add a log message to the container"""
        timestamp = time.strftime("%H:%M:%S")
        log_text = ft.Text(f"[{timestamp}] {message}", color=color, size=12)
        self.log_container.content.controls.append(log_text)
        self.page.update()
        
        # Auto-scroll to bottom
        if len(self.log_container.content.controls) > 50:
            self.log_container.content.controls.pop(0)
    
    def clear_logs(self, e):
        """Clear all log messages"""
        self.log_container.content.controls.clear()
        self.page.update()
    
    def connect_to_database(self, e):
        """Connect to the Neon database"""
        def connect():
            try:
                self.log_message("Attempting to connect to Neon database...", ft.colors.BLUE)
                self.connection = psycopg2.connect(self.connection_string)
                self.connection_status.value = "Connected ✓"
                self.connection_status.color = ft.colors.GREEN
                self.create_tables_btn.disabled = False
                self.log_message("Successfully connected to database!", ft.colors.GREEN)
                self.page.update()
            except Exception as ex:
                self.connection_status.value = f"Connection failed: {str(ex)}"
                self.connection_status.color = ft.colors.RED
                self.log_message(f"Connection failed: {str(ex)}", ft.colors.RED)
                self.page.update()
        
        # Run connection in thread to avoid blocking UI
        threading.Thread(target=connect).start()
    
    def create_all_tables(self, e):
        """Create all database tables"""
        def create_tables():
            if not self.connection:
                self.log_message("No database connection!", ft.colors.RED)
                return
            
            self.progress_bar.visible = True
            self.progress_text.visible = True
            self.progress_bar.value = 0
            self.page.update()
            
            try:
                cursor = self.connection.cursor()
                
                # Define all SQL commands in order
                sql_commands = self.get_sql_commands()
                total_commands = len(sql_commands)
                
                for i, (description, sql) in enumerate(sql_commands):
                    try:
                        self.log_message(f"Creating {description}...", ft.colors.BLUE)
                        cursor.execute(sql)
                        self.connection.commit()
                        self.log_message(f"✓ {description} created successfully", ft.colors.GREEN)
                        
                        # Update progress
                        progress = (i + 1) / total_commands
                        self.progress_bar.value = progress
                        self.progress_text.value = f"Progress: {i+1}/{total_commands} ({int(progress*100)}%)"
                        self.page.update()
                        
                    except Exception as ex:
                        self.log_message(f"✗ Failed to create {description}: {str(ex)}", ft.colors.RED)
                        self.connection.rollback()
                
                cursor.close()
                self.log_message("Database setup completed!", ft.colors.GREEN)
                self.progress_text.value = "Setup Complete!"
                
            except Exception as ex:
                self.log_message(f"Error during table creation: {str(ex)}", ft.colors.RED)
            
            finally:
                self.progress_bar.visible = False
                self.page.update()
        
        # Run table creation in thread
        threading.Thread(target=create_tables).start()
    
    def get_sql_commands(self):
        """Return list of (description, sql) tuples for database creation"""
        return [
            ("Users table", """
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255),
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    role VARCHAR(20) NOT NULL DEFAULT 'STAFF' CHECK (role IN ('ADMIN', 'MANAGER', 'STAFF', 'AGENT')),
                    is_active BOOLEAN DEFAULT TRUE,
                    last_login TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """),
            
            ("Categories table", """
                CREATE TABLE IF NOT EXISTS categories (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    parent_id VARCHAR(30),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
                )
            """),
            
            ("Products table", """
                CREATE TABLE IF NOT EXISTS products (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    sku VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    category_id VARCHAR(30) NOT NULL,
                    unit_of_measure VARCHAR(20) DEFAULT 'pcs',
                    weight DECIMAL(10,3),
                    dimensions VARCHAR(50),
                    cost_price DECIMAL(12,2),
                    selling_price DECIMAL(12,2),
                    min_stock_level INTEGER DEFAULT 0,
                    max_stock_level INTEGER DEFAULT 1000,
                    reorder_point INTEGER DEFAULT 10,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
                )
            """),
            
            ("Warehouses table", """
                CREATE TABLE IF NOT EXISTS warehouses (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    code VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    address TEXT,
                    contact_person VARCHAR(100),
                    phone VARCHAR(20),
                    email VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """),
            
            ("Inventory table", """
                CREATE TABLE IF NOT EXISTS inventory (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    product_id VARCHAR(30) NOT NULL,
                    warehouse_id VARCHAR(30) NOT NULL,
                    quantity_on_hand INTEGER DEFAULT 0,
                    quantity_reserved INTEGER DEFAULT 0,
                    last_updated TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE,
                    UNIQUE(product_id, warehouse_id)
                )
            """),
            
            ("Stock movements table", """
                CREATE TABLE IF NOT EXISTS stock_movements (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    product_id VARCHAR(30) NOT NULL,
                    warehouse_id VARCHAR(30) NOT NULL,
                    movement_type VARCHAR(20) NOT NULL CHECK (movement_type IN ('IN', 'OUT', 'TRANSFER', 'ADJUSTMENT')),
                    quantity INTEGER NOT NULL,
                    reference_type VARCHAR(20) NOT NULL CHECK (reference_type IN ('PURCHASE', 'SALE', 'PRODUCTION', 'ADJUSTMENT', 'TRANSFER')),
                    reference_id VARCHAR(30),
                    unit_cost DECIMAL(12,2),
                    total_cost DECIMAL(12,2),
                    notes TEXT,
                    created_by VARCHAR(30),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (warehouse_id) REFERENCES warehouses(id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
                )
            """),
            
            ("Customers table", """
                CREATE TABLE IF NOT EXISTS customers (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    customer_code VARCHAR(20) UNIQUE NOT NULL,
                    company_name VARCHAR(200),
                    contact_person VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    billing_address TEXT,
                    shipping_address TEXT,
                    credit_limit DECIMAL(12,2) DEFAULT 0,
                    payment_terms VARCHAR(50),
                    tax_id VARCHAR(50),
                    customer_type VARCHAR(20) DEFAULT 'RETAIL' CHECK (customer_type IN ('RETAIL', 'WHOLESALE', 'DISTRIBUTOR')),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """),
            
            ("Agents table", """
                CREATE TABLE IF NOT EXISTS agents (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    agent_code VARCHAR(20) UNIQUE NOT NULL,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE,
                    phone VARCHAR(20),
                    address TEXT,
                    commission_rate DECIMAL(5,2) DEFAULT 0,
                    territory VARCHAR(100),
                    manager_id VARCHAR(30),
                    hire_date DATE,
                    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'TERMINATED')),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (manager_id) REFERENCES agents(id) ON DELETE SET NULL
                )
            """),
            
            ("Sales orders table", """
                CREATE TABLE IF NOT EXISTS sales_orders (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    customer_id VARCHAR(30) NOT NULL,
                    agent_id VARCHAR(30),
                    order_date DATE NOT NULL,
                    delivery_date DATE,
                    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED')),
                    subtotal DECIMAL(12,2) DEFAULT 0,
                    tax_amount DECIMAL(12,2) DEFAULT 0,
                    discount_amount DECIMAL(12,2) DEFAULT 0,
                    total_amount DECIMAL(12,2) DEFAULT 0,
                    payment_status VARCHAR(20) DEFAULT 'PENDING' CHECK (payment_status IN ('PENDING', 'PARTIAL', 'PAID', 'OVERDUE')),
                    notes TEXT,
                    created_by VARCHAR(30),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT,
                    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE SET NULL,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
                )
            """),
            
            ("Sales order items table", """
                CREATE TABLE IF NOT EXISTS sales_order_items (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    sales_order_id VARCHAR(30) NOT NULL,
                    product_id VARCHAR(30) NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(12,2) NOT NULL,
                    discount_percent DECIMAL(5,2) DEFAULT 0,
                    line_total DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_percent/100)) STORED,
                    FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
                )
            """),
            
            ("Agent commissions table", """
                CREATE TABLE IF NOT EXISTS agent_commissions (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    agent_id VARCHAR(30) NOT NULL,
                    sales_order_id VARCHAR(30) NOT NULL,
                    commission_amount DECIMAL(12,2) NOT NULL,
                    commission_rate DECIMAL(5,2) NOT NULL,
                    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PAID', 'CANCELLED')),
                    payment_date DATE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
                    FOREIGN KEY (sales_order_id) REFERENCES sales_orders(id) ON DELETE CASCADE
                )
            """),
            
            ("Suppliers table", """
                CREATE TABLE IF NOT EXISTS suppliers (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    supplier_code VARCHAR(20) UNIQUE NOT NULL,
                    company_name VARCHAR(200) NOT NULL,
                    contact_person VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    address TEXT,
                    payment_terms VARCHAR(50),
                    tax_id VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """),
            
            ("Purchase orders table", """
                CREATE TABLE IF NOT EXISTS purchase_orders (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    po_number VARCHAR(50) UNIQUE NOT NULL,
                    supplier_id VARCHAR(30) NOT NULL,
                    order_date DATE NOT NULL,
                    expected_delivery_date DATE,
                    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'CONFIRMED', 'RECEIVED', 'CANCELLED')),
                    subtotal DECIMAL(12,2) DEFAULT 0,
                    tax_amount DECIMAL(12,2) DEFAULT 0,
                    total_amount DECIMAL(12,2) DEFAULT 0,
                    notes TEXT,
                    created_by VARCHAR(30),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE RESTRICT,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
                )
            """),
            
            ("Purchase order items table", """
                CREATE TABLE IF NOT EXISTS purchase_order_items (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    purchase_order_id VARCHAR(30) NOT NULL,
                    product_id VARCHAR(30) NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_cost DECIMAL(12,2) NOT NULL,
                    line_total DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
                    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
                )
            """),
            
            ("Production orders table", """
                CREATE TABLE IF NOT EXISTS production_orders (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    order_number VARCHAR(50) UNIQUE NOT NULL,
                    product_id VARCHAR(30) NOT NULL,
                    quantity_to_produce INTEGER NOT NULL,
                    quantity_produced INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'PLANNED' CHECK (status IN ('PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
                    planned_start_date DATE,
                    planned_end_date DATE,
                    actual_start_date DATE,
                    actual_end_date DATE,
                    priority VARCHAR(20) DEFAULT 'MEDIUM' CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
                    notes TEXT,
                    created_by VARCHAR(30),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
                    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
                )
            """),
            
            ("Bill of materials table", """
                CREATE TABLE IF NOT EXISTS bill_of_materials (
                    id VARCHAR(30) PRIMARY KEY DEFAULT gen_random_uuid()::text,
                    finished_product_id VARCHAR(30) NOT NULL,
                    raw_material_id VARCHAR(30) NOT NULL,
                    quantity_required DECIMAL(10,3) NOT NULL,
                    unit_cost DECIMAL(12,2),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    FOREIGN KEY (finished_product_id) REFERENCES products(id) ON DELETE CASCADE,
                    FOREIGN KEY (raw_material_id) REFERENCES products(id) ON DELETE CASCADE,
                    UNIQUE(finished_product_id, raw_material_id)
                )
            """),
            
            # Indexes
            ("Product indexes", """
                CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
                CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
                CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active);
            """),
            
            ("Inventory indexes", """
                CREATE INDEX IF NOT EXISTS idx_inventory_product_warehouse ON inventory(product_id, warehouse_id);
                CREATE INDEX IF NOT EXISTS idx_inventory_low_stock ON inventory(quantity_on_hand) WHERE quantity_on_hand <= 10;
            """),
            
            ("Stock movement indexes", """
                CREATE INDEX IF NOT EXISTS idx_stock_movements_product_date ON stock_movements(product_id, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_stock_movements_warehouse ON stock_movements(warehouse_id);
                CREATE INDEX IF NOT EXISTS idx_stock_movements_reference ON stock_movements(reference_type, reference_id);
            """),
            
            ("Sales order indexes", """
                CREATE INDEX IF NOT EXISTS idx_sales_orders_customer ON sales_orders(customer_id);
                CREATE INDEX IF NOT EXISTS idx_sales_orders_agent ON sales_orders(agent_id);
                CREATE INDEX IF NOT EXISTS idx_sales_orders_date ON sales_orders(order_date DESC);
                CREATE INDEX IF NOT EXISTS idx_sales_orders_status ON sales_orders(status);
            """),
            
            # Triggers
            ("Update timestamp function", """
                CREATE OR REPLACE FUNCTION update_updated_at_column()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.updated_at = NOW();
                    RETURN NEW;
                END;
                $$ language 'plpgsql';
            """),
            
            ("Timestamp triggers", """
                CREATE TRIGGER IF NOT EXISTS update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                CREATE TRIGGER IF NOT EXISTS update_categories_updated_at BEFORE UPDATE ON categories FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                CREATE TRIGGER IF NOT EXISTS update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                CREATE TRIGGER IF NOT EXISTS update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                CREATE TRIGGER IF NOT EXISTS update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                CREATE TRIGGER IF NOT EXISTS update_sales_orders_updated_at BEFORE UPDATE ON sales_orders FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                CREATE TRIGGER IF NOT EXISTS update_suppliers_updated_at BEFORE UPDATE ON suppliers FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                CREATE TRIGGER IF NOT EXISTS update_purchase_orders_updated_at BEFORE UPDATE ON purchase_orders FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
                CREATE TRIGGER IF NOT EXISTS update_production_orders_updated_at BEFORE UPDATE ON production_orders FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();
            """),
            
            # Sample data
            ("Sample data - Admin user", """
                INSERT INTO users (username, email, first_name, last_name, role) VALUES
                ('admin', 'admin@terrainjoy.com', 'Admin', 'User', 'ADMIN')
                ON CONFLICT (username) DO NOTHING;
            """),
            
            ("Sample data - Categories", """
                INSERT INTO categories (name, description) VALUES
                ('Electronics', 'Electronic devices and components'),
                ('Clothing', 'Apparel and accessories'),
                ('Books', 'Books and publications'),
                ('Tools', 'Hardware tools and equipment'),
                ('Office Supplies', 'Office and stationery items')
                ON CONFLICT DO NOTHING;
            """),
            
            ("Sample data - Warehouse", """
                INSERT INTO warehouses (code, name, address, contact_person, phone, email) VALUES
                ('WH001', 'Main Warehouse', '123 Industrial Ave, Business District', 'John Smith', '+1-555-0123', 'warehouse@terrainjoy.com')
                ON CONFLICT (code) DO NOTHING;
            """),
            
            ("Sample data - Supplier", """
                INSERT INTO suppliers (supplier_code, company_name, contact_person, email, phone, payment_terms) VALUES
                ('SUP001', 'Global Supplies Inc.', 'Jane Doe', 'jane@globalsupplies.com', '+1-555-0124', 'Net 30')
                ON CONFLICT (supplier_code) DO NOTHING;
            """),
            
            ("Sample data - Customer", """
                INSERT INTO customers (customer_code, company_name, contact_person, email, phone, customer_type) VALUES
                ('CUS001', 'Retail Plus Store', 'Mike Johnson', 'mike@retailplus.com', '+1-555-0125', 'RETAIL')
                ON CONFLICT (customer_code) DO NOTHING;
            """),
            
            ("Sample data - Agent", """
                INSERT INTO agents (agent_code, first_name, last_name, email, phone, commission_rate, territory) VALUES
                ('AGT001', 'Sarah', 'Wilson', 'sarah@terrainjoy.com', '+1-555-0126', 5.00, 'North Region')
                ON CONFLICT (agent_code) DO NOTHING;
            """)
        ]

if __name__ == "__main__":
    app = DatabaseCreator()
    ft.app(target=app.main)