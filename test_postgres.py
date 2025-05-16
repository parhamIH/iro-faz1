import psycopg2
from psycopg2 import OperationalError

def test_connection():
    try:
        # Connect to PostgreSQL
        connection = psycopg2.connect(
            database="iro1",
            user="parham",
            password="parhams",
            host="localhost",
            port="5432"
        )
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Execute a simple query to get version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print("PostgreSQL connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        # Get list of tables in the database
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table[0]}")
        
        # Close cursor and connection
        cursor.close()
        connection.close()
        
    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_connection() 