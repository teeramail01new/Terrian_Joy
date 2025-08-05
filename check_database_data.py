import psycopg2
import sys

def check_database_data():
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("🔍 Checking database connection and data...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"📋 Found {len(tables)} tables:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Table: {table_name}")
            
            # Get table structure
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            columns = cursor.fetchall()
            print(f"   Columns: {', '.join([f'{col[0]} ({col[1]})' for col in columns])}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   Records: {count}")
            
            # Show sample data (first 3 rows)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                sample_data = cursor.fetchall()
                print(f"   Sample data:")
                for i, row in enumerate(sample_data, 1):
                    print(f"     Row {i}: {row}")
            else:
                print(f"   ⚠️  No data in table")
        
        cursor.close()
        connection.close()
        print("\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    check_database_data() 