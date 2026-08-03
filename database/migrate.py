from database.connection import get_connection

def migrate():
    conn = get_connection()
    cursor = conn.cursor()

    with open("database/schema.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Database schema created.")

if __name__ == "__main__":
    migrate()