#!/usr/bin/env python3
"""
Simple script to set up the Terrain Joy database tables
Run this if the main program shows "Tables not found" message
"""

import psycopg2
import sys

def setup_database():
    """Set up the database tables"""
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("Connecting to Neon database...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        print("✓ Connected to database successfully!")
        
        # Check if tables already exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'products'
            ) as exists
        """)
        
        tables_exist = cursor.fetchone()[0]
        
        if tables_exist:
            print("✓ Database tables already exist!")
            print("You can now run the main program: python main_program_terrian.py")
        else:
            print("Creating database tables...")
            
            # Import the database creator
            sys.path.append('terrain_joy_db_creator')
            from create_database_terrian import DatabaseCreator
            
            creator = DatabaseCreator()
            creator.connection = connection
            
            # Get SQL commands
            sql_commands = creator.get_sql_commands()
            
            for i, (description, sql) in enumerate(sql_commands):
                try:
                    print(f"Creating {description}...")
                    cursor.execute(sql)
                    connection.commit()
                    print(f"✓ {description} created successfully")
                except Exception as e:
                    print(f"✗ Failed to create {description}: {e}")
                    connection.rollback()
            
            print("\n✓ Database setup completed!")
            print("You can now run the main program: python main_program_terrian.py")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("Please check your connection string and try again.")

if __name__ == "__main__":
    setup_database() 