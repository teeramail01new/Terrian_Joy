import flet as ft
import psycopg2
from datetime import datetime, date
import threading
from typing import List, Optional, Dict, Any
import sys
import os

# Database Manager Class
class DatabaseManager:
    def __init__(self):
        self.connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
        self.connection = None
        self.is_connected = False
    
    def connect(self):
        try:
            self.connection = psycopg2.connect(self.connection_string)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.is_connected = False
            return False
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        try:
            if not self.connection or self.connection.closed:
                if not self.connect():
                    return None
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                if cursor.description:  # Check if there are columns
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in result]
                return []
            else:
                self.connection.commit()
                return True
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            print(f"Query error: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def close(self):
        if self.connection:
            self.connection.close()
            self.is_connected = False

# Main Application Class
class TerrainJoyStockApp:
    def __init__(self):
        self.db = DatabaseManager()
        self.current_page = "dashboard"
        self.page = None
        self.nav_rail = None
        self.content_area = None
        self.status_bar = None
        
        # UI Colors and Theme
        self.primary_color = ft.Colors.BLUE_700
        self.secondary_color = ft.Colors.BLUE_50
        self.accent_color = ft.Colors.ORANGE_600
        self.success_color = ft.Colors.GREEN_600
        self.error_color = ft.Colors.RED_600
        self.warning_color = ft.Colors.ORANGE_600
        
    def main(self, page: ft.Page):
        self.page = page
        
        # Configure page settings for Windows standalone
        page.title = "Terrain Joy - Stock Management System"
        page.window_width = 1400
        page.window_height = 900
        page.window_min_width = 1200
        page.window_min_height = 700
        page.window_maximizable = True
        page.window_resizable = True
        page.padding = 0
        page.spacing = 0
        
        # Set theme
        page.theme_mode = ft.ThemeMode.LIGHT
        page.theme = ft.Theme(
            color_scheme_seed=self.primary_color,
        )
        
        # Initialize database connection
        self.init_database_connection()
        
        # Create main layout
        self.create_navigation()
        self.create_content_area()
        self.create_status_bar()
        
        # Build main layout
        main_container = ft.Container(
            content=ft.Column([
                self.create_header(),
                ft.Container(
                    content=ft.Row([
                        self.nav_rail,
                        ft.VerticalDivider(width=1, color=ft.Colors.GREY_300),
                        self.content_area,
                    ], expand=True, spacing=0),
                    expand=True,
                ),
                self.status_bar,
            ], spacing=0),
            expand=True,
            bgcolor=ft.Colors.GREY_50,
        )
        
        page.add(main_container)
        
        # Load initial content
        self.update_content()
        
        # Handle window close
        page.window_prevent_close = True
        page.on_window_event = self.on_window_event
    
    def on_window_event(self, e):
        if e.data == "close":
            self.handle_app_close()
    
    def handle_app_close(self):
        def close_app(e):
            self.db.close()
            self.page.window_destroy()
        
        def cancel_close(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Exit"),
            content=ft.Text("Are you sure you want to close Terrain Joy Stock Management?"),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_close),
                ft.ElevatedButton("Exit", on_click=close_app, bgcolor=self.error_color, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def init_database_connection(self):
        """Initialize database connection with loading indicator"""
        self.update_status("Connecting to database...", self.warning_color)
        
        # Try to connect immediately
        if self.db.connect():
            # Check if tables exist
            tables_exist = self.check_database_tables()
            if tables_exist:
                self.update_status("Connected to database", self.success_color)
            else:
                self.update_status("Connected to database - Tables not found. Run database setup first.", self.warning_color)
        else:
            self.update_status("Failed to connect to database", self.error_color)
    
    def check_database_tables(self):
        """Check if required tables exist in the database"""
        try:
            # Check for at least one of the main tables
            result = self.db.execute_query("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'products'
                ) as exists
            """)
            return result and result[0]['exists']
        except Exception as e:
            print(f"Error checking tables: {e}")
            return False
    
    def create_header(self):
        """Create application header"""
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.INVENTORY, size=32, color=self.primary_color),
                    ft.Text(
                        "Terrain Joy",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=self.primary_color,
                    ),
                    ft.Text(
                        "Stock Management System",
                        size=16,
                        color=ft.Colors.GREY_600,
                    ),
                ], spacing=10),
                
                ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.PERSON, size=20, color=ft.Colors.WHITE),
                            ft.Text("Administrator", color=ft.Colors.WHITE, size=14),
                        ], spacing=5),
                        bgcolor=self.primary_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=20,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        tooltip="Settings",
                        on_click=self.show_settings,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh Data",
                        on_click=self.refresh_data,
                    ),
                ], spacing=5),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=15),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(bottom=ft.BorderSide(2, ft.Colors.GREY_200)),
        )
    
    def create_navigation(self):
        """Create navigation rail with beautiful design"""
        self.nav_rail = ft.Container(
            content=ft.NavigationRail(
                selected_index=0,
                label_type=ft.NavigationRailLabelType.ALL,
                min_width=200,
                min_extended_width=200,
                group_alignment=-0.9,
                destinations=[
                    ft.NavigationRailDestination(
                        icon=ft.Icons.DASHBOARD_OUTLINED,
                        selected_icon=ft.Icons.DASHBOARD,
                        label="Dashboard",
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icons.INVENTORY_OUTLINED,
                        selected_icon=ft.Icons.INVENTORY,
                        label="Products",
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icons.WAREHOUSE_OUTLINED,
                        selected_icon=ft.Icons.WAREHOUSE,
                        label="Inventory",
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                        selected_icon=ft.Icons.RECEIPT_LONG,
                        label="Stock Moves",
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icons.SHOPPING_CART_OUTLINED,
                        selected_icon=ft.Icons.SHOPPING_CART,
                        label="Sales Orders",
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icons.PEOPLE_OUTLINED,
                        selected_icon=ft.Icons.PEOPLE,
                        label="Customers",
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icons.PERSON_OUTLINED,
                        selected_icon=ft.Icons.PERSON,
                        label="Agents",
                    ),
                    ft.NavigationRailDestination(
                        icon=ft.Icons.ANALYTICS_OUTLINED,
                        selected_icon=ft.Icons.ANALYTICS,
                        label="Reports",
                    ),
                ],
                on_change=self.nav_change,
                bgcolor=ft.Colors.WHITE,
                indicator_color=self.secondary_color,
                selected_label_text_style=ft.TextStyle(
                    color=self.primary_color,
                    weight=ft.FontWeight.BOLD,
                ),
                unselected_label_text_style=ft.TextStyle(
                    color=ft.Colors.GREY_600,
                ),
            ),
            width=200,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_200)),
        )
    
    def create_content_area(self):
        """Create main content area"""
        self.content_area = ft.Container(
            content=ft.Column([
                ft.Text("Loading...", size=20),
                ft.ProgressRing(),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=20,
            bgcolor=ft.Colors.GREY_50,
        )
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8, color=self.success_color),
                    ft.Text("Ready", size=12, color=ft.Colors.GREY_600),
                ], spacing=5),
                
                ft.Row([
                    ft.Text(f"Version 1.0.0", size=12, color=ft.Colors.GREY_600),
                    ft.Text("•", size=12, color=ft.Colors.GREY_400),
                    ft.Text(f"© 2024 Terrain Joy", size=12, color=ft.Colors.GREY_600),
                ], spacing=5),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_200)),
        )
    
    def update_status(self, message: str, color: str = None):
        """Update status bar message"""
        if self.status_bar and hasattr(self.status_bar.content, 'controls'):
            status_icon = self.status_bar.content.controls[0].controls[0]
            status_text = self.status_bar.content.controls[0].controls[1]
            
            status_text.value = message
            if color:
                status_icon.color = color
            
            if self.page:
                self.page.update()
    
    def nav_change(self, e):
        """Handle navigation changes"""
        pages = ["dashboard", "products", "inventory", "stock_moves", "sales", "customers", "agents", "reports"]
        self.current_page = pages[e.control.selected_index]
        self.update_content()
        self.update_status(f"Switched to {self.current_page.title()}")
    
    def update_content(self):
        """Update main content area based on current page"""
        def load_content():
            try:
                if self.current_page == "dashboard":
                    content = self.get_dashboard_content()
                elif self.current_page == "products":
                    content = self.get_products_content()
                elif self.current_page == "inventory":
                    content = self.get_inventory_content()
                elif self.current_page == "stock_moves":
                    content = self.get_stock_moves_content()
                elif self.current_page == "sales":
                    content = self.get_sales_content()
                elif self.current_page == "customers":
                    content = self.get_customers_content()
                elif self.current_page == "agents":
                    content = self.get_agents_content()
                elif self.current_page == "reports":
                    content = self.get_reports_content()
                else:
                    content = self.get_dashboard_content()
                
                self.content_area.content = content
                if self.page:
                    self.page.update()
                    
            except Exception as e:
                print(f"Error loading content for {self.current_page}: {e}")
                error_content = ft.Column([
                    ft.Icon(ft.Icons.ERROR, size=64, color=self.error_color),
                    ft.Text("Error Loading Content", size=24, weight=ft.FontWeight.BOLD, color=self.error_color),
                    ft.Text(f"Error: {str(e)}", size=14, color=ft.Colors.GREY_600),
                    ft.Text("Please check database connection and try again.", size=12, color=ft.Colors.GREY_500),
                    ft.ElevatedButton(
                        "Retry",
                        icon=ft.Icons.REFRESH,
                        on_click=lambda _: self.update_content(),
                        bgcolor=self.primary_color,
                        color=ft.Colors.WHITE,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                
                self.content_area.content = error_content
                if self.page:
                    self.page.update()
        
        # Show loading state
        self.content_area.content = ft.Column([
            ft.ProgressRing(color=self.primary_color),
            ft.Text(f"Loading {self.current_page.title()}...", size=16, color=ft.Colors.GREY_600),
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        
        if self.page:
            self.page.update()
        
        # Load content in background thread
        threading.Thread(target=load_content, daemon=True).start()
    
    def create_page_header(self, title: str, subtitle: str = None, actions: List = None):
        """Create standardized page header"""
        header_content = [
            ft.Column([
                ft.Text(title, size=32, weight=ft.FontWeight.BOLD, color=self.primary_color),
                *([ft.Text(subtitle, size=16, color=ft.Colors.GREY_600)] if subtitle else []),
            ], spacing=5),
        ]
        
        if actions:
            header_content.append(ft.Row(actions, spacing=10))
        
        return ft.Container(
            content=ft.Row(
                header_content,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=20),
        )
    
    def create_stat_card(self, title: str, value: str, icon: str, color: str, subtitle: str = None):
        """Create beautiful statistic cards"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=40, color=color),
                    ft.Column([
                        ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
                        ft.Text(title, size=14, color=ft.Colors.GREY_600),
                        *([ft.Text(subtitle, size=12, color=ft.Colors.GREY_500)] if subtitle else []),
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.END),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ]),
            width=280,
            height=120,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )
    
    def create_data_table(self, data: List[Dict], columns: List[Dict], title: str = None):
        """Create a data table with the given data and columns"""
        if not data:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=48, color=ft.Colors.GREY_400),
                    ft.Text("No data available", size=16, color=ft.Colors.GREY_600),
                    ft.Text("Add some data to see it here", size=14, color=ft.Colors.GREY_500),
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            )
        
        # Create table rows
        table_rows = []
        
        # Header row
        header_cells = []
        for col in columns:
            header_cells.append(
                ft.DataCell(
                    ft.Text(
                        col['label'],
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700,
                        size=14
                    )
                )
            )
        table_rows.append(ft.DataRow(cells=header_cells))
        
        # Data rows
        for row_data in data:
            cells = []
            for col in columns:
                value = row_data.get(col['field'], '')
                if isinstance(value, (int, float)):
                    value = str(value)
                elif value is None:
                    value = '-'
                
                # Truncate long values
                if len(str(value)) > 30:
                    value = str(value)[:27] + "..."
                
                cells.append(ft.DataCell(ft.Text(value, size=13)))
            table_rows.append(ft.DataRow(cells=cells))
        
        return ft.Container(
            content=ft.Column([
                ft.Text(title or "Data", size=18, weight=ft.FontWeight.BOLD, color=self.primary_color),
                ft.Divider(color=ft.Colors.GREY_300),
                ft.DataTable(
                    columns=len(columns),
                    rows=table_rows,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    column_spacing=20,
                    heading_row_height=50,
                    data_row_min_height=40,
                    data_row_max_height=50,
                    divider_thickness=1,
                    horizontal_lines=ft.border.BorderSide(1, ft.Colors.GREY_200),
                    heading_text_style=ft.TextStyle(
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_700,
                    ),
                    data_text_style=ft.TextStyle(
                        size=13,
                        color=ft.Colors.GREY_800,
                    ),
                ),
            ]),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )
    
    # Content Methods for Different Pages
    def get_dashboard_content(self):
        """Dashboard content with overview statistics"""
        stats = self.get_dashboard_stats()
        
        # Statistics cards
        stats_row = ft.Row([
            self.create_stat_card(
                "Total Products", 
                str(stats.get('total_products', 0)), 
                ft.Icons.INVENTORY, 
                self.primary_color,
                "Active items"
            ),
            self.create_stat_card(
                "Low Stock Items", 
                str(stats.get('low_stock', 0)), 
                ft.Icons.WARNING, 
                self.error_color,
                "Need reorder"
            ),
            self.create_stat_card(
                "Total Customers", 
                str(stats.get('total_customers', 0)), 
                ft.Icons.PEOPLE, 
                self.success_color,
                "Active accounts"
            ),
            self.create_stat_card(
                "Active Agents", 
                str(stats.get('total_agents', 0)), 
                ft.Icons.PERSON, 
                self.accent_color,
                "Sales team"
            ),
        ], spacing=20, wrap=True)
        
        # Recent activities
        recent_section = ft.Container(
            content=ft.Column([
                ft.Text("Recent Activities", size=20, weight=ft.FontWeight.BOLD, color=self.primary_color),
                ft.Divider(color=ft.Colors.GREY_300),
                ft.Text("Recent stock movements and sales activities will appear here.", 
                       size=14, color=ft.Colors.GREY_600),
            ]),
            width=None,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )
        
        return ft.Column([
            self.create_page_header(
                "Dashboard", 
                "Welcome to Terrain Joy Stock Management System"
            ),
            stats_row,
            ft.Container(height=30),
            recent_section,
        ], scroll=ft.ScrollMode.AUTO)
    
    def get_products_content(self):
        """Products management content with data grid"""
        add_button = ft.ElevatedButton(
            "Add Product",
                            icon=ft.Icons.ADD,
            bgcolor=self.primary_color,
            color=ft.Colors.WHITE,
            on_click=self.show_add_product_dialog,
        )
        
        # Get products data
        products_data = self.get_products_data()
        products_columns = [
            {'field': 'sku', 'label': 'SKU'},
            {'field': 'name', 'label': 'Product Name'},
            {'field': 'category_name', 'label': 'Category'},
            {'field': 'selling_price', 'label': 'Price'},
            {'field': 'unit_of_measure', 'label': 'Unit'},
            {'field': 'is_active', 'label': 'Status'},
        ]
        
        return ft.Column([
            self.create_page_header("Products", "Manage your product catalog", [add_button]),
            self.create_data_table(products_data, products_columns, "Products List"),
        ], scroll=ft.ScrollMode.AUTO)
    
    def get_inventory_content(self):
        """Inventory management content with data grid"""
        # Get inventory data
        inventory_data = self.get_inventory_data()
        inventory_columns = [
            {'field': 'product_name', 'label': 'Product'},
            {'field': 'warehouse_name', 'label': 'Warehouse'},
            {'field': 'quantity_on_hand', 'label': 'On Hand'},
            {'field': 'quantity_reserved', 'label': 'Reserved'},
            {'field': 'available_qty', 'label': 'Available'},
            {'field': 'last_updated', 'label': 'Last Updated'},
        ]
        
        return ft.Column([
            self.create_page_header("Inventory", "Monitor and manage stock levels"),
            self.create_data_table(inventory_data, inventory_columns, "Inventory Levels"),
        ], scroll=ft.ScrollMode.AUTO)
    
    def get_stock_moves_content(self):
        """Stock movements content with data grid"""
        # Get stock movements data
        movements_data = self.get_stock_movements_data()
        movements_columns = [
            {'field': 'product_name', 'label': 'Product'},
            {'field': 'warehouse_name', 'label': 'Warehouse'},
            {'field': 'movement_type', 'label': 'Type'},
            {'field': 'quantity', 'label': 'Quantity'},
            {'field': 'reference_type', 'label': 'Reference'},
            {'field': 'created_at', 'label': 'Date'},
        ]
        
        return ft.Column([
            self.create_page_header("Stock Movements", "Track all inventory transactions"),
            self.create_data_table(movements_data, movements_columns, "Recent Stock Movements"),
        ], scroll=ft.ScrollMode.AUTO)
    
    def get_sales_content(self):
        """Sales orders content with data grid"""
        add_order_button = ft.ElevatedButton(
            "New Order",
                            icon=ft.Icons.ADD_SHOPPING_CART,
            bgcolor=self.success_color,
            color=ft.Colors.WHITE,
            on_click=self.show_add_order_dialog,
        )
        
        # Get sales orders data
        sales_data = self.get_sales_orders_data()
        sales_columns = [
            {'field': 'order_number', 'label': 'Order #'},
            {'field': 'customer_name', 'label': 'Customer'},
            {'field': 'agent_name', 'label': 'Agent'},
            {'field': 'order_date', 'label': 'Order Date'},
            {'field': 'status', 'label': 'Status'},
            {'field': 'total_amount', 'label': 'Total'},
        ]
        
        return ft.Column([
            self.create_page_header("Sales Orders", "Manage customer orders", [add_order_button]),
            self.create_data_table(sales_data, sales_columns, "Sales Orders"),
        ], scroll=ft.ScrollMode.AUTO)
    
    def get_customers_content(self):
        """Customers management content with data grid"""
        add_customer_button = ft.ElevatedButton(
            "Add Customer",
            icon=ft.Icons.PERSON_ADD,
            bgcolor=self.primary_color,
            color=ft.Colors.WHITE,
            on_click=self.show_add_customer_dialog,
        )
        
        # Get customers data
        customers_data = self.get_customers_data()
        customers_columns = [
            {'field': 'customer_code', 'label': 'Code'},
            {'field': 'company_name', 'label': 'Company'},
            {'field': 'contact_person', 'label': 'Contact'},
            {'field': 'email', 'label': 'Email'},
            {'field': 'phone', 'label': 'Phone'},
            {'field': 'customer_type', 'label': 'Type'},
            {'field': 'is_active', 'label': 'Status'},
        ]
        
        return ft.Column([
            self.create_page_header("Customers", "Manage customer relationships", [add_customer_button]),
            self.create_data_table(customers_data, customers_columns, "Customers List"),
        ], scroll=ft.ScrollMode.AUTO)
    
    def get_agents_content(self):
        """Agents management content with data grid"""
        add_agent_button = ft.ElevatedButton(
            "Add Agent",
            icon=ft.Icons.PERSON_ADD,
            bgcolor=self.accent_color,
            color=ft.Colors.WHITE,
            on_click=self.show_add_agent_dialog,
        )
        
        # Get agents data
        agents_data = self.get_agents_data()
        agents_columns = [
            {'field': 'agent_code', 'label': 'Code'},
            {'field': 'full_name', 'label': 'Name'},
            {'field': 'email', 'label': 'Email'},
            {'field': 'phone', 'label': 'Phone'},
            {'field': 'territory', 'label': 'Territory'},
            {'field': 'commission_rate', 'label': 'Commission %'},
            {'field': 'status', 'label': 'Status'},
        ]
        
        return ft.Column([
            self.create_page_header("Agents", "Manage sales team", [add_agent_button]),
            self.create_data_table(agents_data, agents_columns, "Sales Agents"),
        ], scroll=ft.ScrollMode.AUTO)
    
    def get_reports_content(self):
        """Reports and analytics content"""
        return ft.Column([
            self.create_page_header("Reports", "Analytics and insights"),
            ft.Container(
                content=ft.Text("Reports and analytics will be displayed here.", size=16),
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
            ),
        ], scroll=ft.ScrollMode.AUTO)
    
    # Database Methods for Data Retrieval
    def get_products_data(self):
        """Get products data for the data grid"""
        try:
            query = """
                SELECT 
                    p.sku,
                    p.name,
                    c.name as category_name,
                    p.selling_price,
                    p.unit_of_measure,
                    CASE WHEN p.is_active THEN 'Active' ELSE 'Inactive' END as is_active
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                ORDER BY p.name
                LIMIT 50
            """
            result = self.db.execute_query(query)
            return result if result is not None else []
        except Exception as e:
            print(f"Error getting products data: {e}")
            return []
    
    def get_inventory_data(self):
        """Get inventory data for the data grid"""
        try:
            query = """
                SELECT 
                    p.name as product_name,
                    w.name as warehouse_name,
                    i.quantity_on_hand,
                    i.quantity_reserved,
                    (i.quantity_on_hand - i.quantity_reserved) as available_qty,
                    i.last_updated
                FROM inventory i
                JOIN products p ON i.product_id = p.id
                JOIN warehouses w ON i.warehouse_id = w.id
                ORDER BY p.name, w.name
                LIMIT 50
            """
            result = self.db.execute_query(query)
            return result if result is not None else []
        except Exception as e:
            print(f"Error getting inventory data: {e}")
            return []
    
    def get_stock_movements_data(self):
        """Get stock movements data for the data grid"""
        try:
            query = """
                SELECT 
                    p.name as product_name,
                    w.name as warehouse_name,
                    sm.movement_type,
                    sm.quantity,
                    sm.reference_type,
                    sm.created_at
                FROM stock_movements sm
                JOIN products p ON sm.product_id = p.id
                JOIN warehouses w ON sm.warehouse_id = w.id
                ORDER BY sm.created_at DESC
                LIMIT 50
            """
            result = self.db.execute_query(query)
            return result if result is not None else []
        except Exception as e:
            print(f"Error getting stock movements data: {e}")
            return []
    
    def get_sales_orders_data(self):
        """Get sales orders data for the data grid"""
        try:
            query = """
                SELECT 
                    so.order_number,
                    c.company_name as customer_name,
                    CONCAT(a.first_name, ' ', a.last_name) as agent_name,
                    so.order_date,
                    so.status,
                    so.total_amount
                FROM sales_orders so
                LEFT JOIN customers c ON so.customer_id = c.id
                LEFT JOIN agents a ON so.agent_id = a.id
                ORDER BY so.order_date DESC
                LIMIT 50
            """
            result = self.db.execute_query(query)
            return result if result is not None else []
        except Exception as e:
            print(f"Error getting sales orders data: {e}")
            return []
    
    def get_customers_data(self):
        """Get customers data for the data grid"""
        try:
            query = """
                SELECT 
                    customer_code,
                    company_name,
                    contact_person,
                    email,
                    phone,
                    customer_type,
                    CASE WHEN is_active THEN 'Active' ELSE 'Inactive' END as is_active
                FROM customers
                ORDER BY company_name
                LIMIT 50
            """
            result = self.db.execute_query(query)
            return result if result is not None else []
        except Exception as e:
            print(f"Error getting customers data: {e}")
            return []
    
    def get_agents_data(self):
        """Get agents data for the data grid"""
        try:
            query = """
                SELECT 
                    agent_code,
                    CONCAT(first_name, ' ', last_name) as full_name,
                    email,
                    phone,
                    territory,
                    commission_rate,
                    status
                FROM agents
                ORDER BY first_name, last_name
                LIMIT 50
            """
            result = self.db.execute_query(query)
            return result if result is not None else []
        except Exception as e:
            print(f"Error getting agents data: {e}")
            return []
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        stats = {
            'total_products': 0,
            'low_stock': 0,
            'total_customers': 0,
            'total_agents': 0,
        }
        
        if not self.db.is_connected:
            print("Database not connected, returning default stats")
            return stats
        
        try:
            # Check if tables exist before querying
            table_checks = [
                ("products", "SELECT COUNT(*) as count FROM products WHERE is_active = true"),
                ("customers", "SELECT COUNT(*) as count FROM customers WHERE is_active = true"),
                ("agents", "SELECT COUNT(*) as count FROM agents WHERE status = 'ACTIVE'"),
            ]
            
            for table_name, query in table_checks:
                try:
                    result = self.db.execute_query(query)
                    if result and len(result) > 0:
                        if table_name == "products":
                            stats['total_products'] = result[0]['count']
                        elif table_name == "customers":
                            stats['total_customers'] = result[0]['count']
                        elif table_name == "agents":
                            stats['total_agents'] = result[0]['count']
                    else:
                        print(f"No results for {table_name} query")
                except Exception as e:
                    print(f"Error querying {table_name} table: {e}")
                    continue
            
            # Low stock items (placeholder for now)
            stats['low_stock'] = 5
                
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
        
        return stats
    
    # Dialog Methods (Placeholder implementations)
    def show_add_product_dialog(self, e):
        self.show_info_dialog("Add Product", "Product creation dialog will be implemented here.")
    
    def show_add_order_dialog(self, e):
        self.show_info_dialog("New Order", "Sales order creation dialog will be implemented here.")
    
    def show_add_customer_dialog(self, e):
        self.show_info_dialog("Add Customer", "Customer creation dialog will be implemented here.")
    
    def show_add_agent_dialog(self, e):
        self.show_info_dialog("Add Agent", "Agent creation dialog will be implemented here.")
    
    def show_settings(self, e):
        self.show_info_dialog("Settings", "Application settings will be available here.")
    
    def refresh_data(self, e):
        self.update_status("Refreshing data...", self.warning_color)
        self.update_content()
        
        def reset_status():
            import time
            time.sleep(2)
            self.update_status("Data refreshed", self.success_color)
        
        threading.Thread(target=reset_status, daemon=True).start()
    
    def show_info_dialog(self, title: str, message: str):
        """Show information dialog"""
        def close_dialog(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, color=self.primary_color),
            content=ft.Text(message),
            actions=[
                ft.ElevatedButton("OK", on_click=close_dialog, bgcolor=self.primary_color, color=ft.Colors.WHITE),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

# Main function to run the Windows standalone application
def main(page: ft.Page):
    app = TerrainJoyStockApp()
    app.main(page)

# Application entry point for Windows standalone
if __name__ == "__main__":
    # Configure for Windows standalone
    ft.app(
        target=main,
        name="Terrain Joy Stock Management",
        assets_dir="assets",  # For icons and images
    )