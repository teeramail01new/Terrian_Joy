#!/usr/bin/env python3
"""
Script to fix the database schema by adding missing fields
"""

import psycopg2

def fix_database_schema():
    """Fix the database schema"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Check if category_id exists in products table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'category_id'
        """)
        
        category_id_exists = cursor.fetchone()
        
        if not category_id_exists:
            print("Adding missing category_id field to products table...")
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN category_id VARCHAR(30) NOT NULL DEFAULT 'CAT001'
            """)
            
            # Add foreign key constraint
            cursor.execute("""
                ALTER TABLE products 
                ADD CONSTRAINT fk_products_category 
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
            """)
            
            print("✓ Added category_id field to products table")
        else:
            print("✓ category_id field already exists in products table")
        
        # Check if description field exists in products table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'description'
        """)
        
        description_exists = cursor.fetchone()
        
        if not description_exists:
            print("Adding missing description field to products table...")
            cursor.execute("""
                ALTER TABLE products 
                ADD COLUMN description TEXT
            """)
            print("✓ Added description field to products table")
        else:
            print("✓ description field already exists in products table")
        
        connection.commit()
        print("✓ Database schema fixed successfully!")
        print("You can now run the sample data script: python add_sample_data.py")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Please check your connection string and try again.")

if __name__ == "__main__":
    fix_database_schema() 