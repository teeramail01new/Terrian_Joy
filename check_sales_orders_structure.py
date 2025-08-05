import psycopg2

def check_sales_orders_structure():
    connection_string = "postgresql://neondb_owner:npg_BidDY7RA4zWX@ep-long-haze-a17mcg70-pooler.ap-southeast-1.aws.neon.tech/terrian_joy?sslmode=require&channel_binding=require"
    
    try:
        print("🔍 Checking sales_orders table structure...")
        connection = psycopg2.connect(connection_string)
        cursor = connection.cursor()
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'sales_orders'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("📋 Sales Orders Table Structure:")
        for col in columns:
            print(f"   {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # Get constraints
        cursor.execute("""
            SELECT conname, contype, pg_get_constraintdef(oid) as definition
            FROM pg_constraint 
            WHERE conrelid = 'sales_orders'::regclass
        """)
        
        constraints = cursor.fetchall()
        print("\n🔒 Constraints:")
        for constraint in constraints:
            print(f"   {constraint[0]}: {constraint[2]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_sales_orders_structure() 