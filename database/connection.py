import sqlite3

DB_NAME = "field_nation_data.db"

def run_sql_query(query: str):
    """ডাটাবেজে SQL Query রান করে রেজাল্ট নিয়ে আসার ফাংশন"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return {"status": "success", "columns": columns, "data": rows}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_db_schema():
    """ডাটাবেজের টেবিল স্ট্রাকচার বা স্কিমা রিটার্ন করে (যা AI Agent-কে বুঝাতে সাহায্য করবে)"""
    schema_info = """
    Table: users
    - user_id: INTEGER (Primary Key)
    - name: TEXT
    - email: TEXT
    - signup_date: TEXT (YYYY-MM-DD)
    - country: TEXT

    Table: sales
    - sale_id: INTEGER (Primary Key)
    - user_id: INTEGER (Foreign Key to users.user_id)
    - product_name: TEXT
    - category: TEXT
    - amount: REAL
    - sale_date: TEXT (YYYY-MM-DD)
    """
    return schema_info
