#!/usr/bin/env python3
"""
Script to debug the database schema and find the exact field causing length issues
"""

import psycopg2

def debug_schema():
    """Debug the database schema"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Check all table structures
        tables = ['categories', 'products', 'warehouses', 'customers', 'agents', 'sales_orders', 'stock_movements']
        
        for table in tables:
            print(f"\n{table.upper()} table structure:")
            cursor.execute(f"""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                ORDER BY ordinal_position
            """)
            
            for row in cursor.fetchall():
                print(f"  {row[0]}: {row[1]} (max length: {row[2]}, nullable: {row[3]})")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    debug_schema() 