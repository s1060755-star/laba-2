import sqlite3

DATABASE = "my_database.db"  # якщо база в цій самій папці, де main.py

def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Таблиця страв ---
def get_all_dishes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM dishes").fetchall()
    conn.close()
    return rows

def get_dish_by_id(dish_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM dishes WHERE id = ?", (dish_id,)).fetchone()
    conn.close()
    return row

# --- Таблиця послуг ---
def get_all_services():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM service").fetchall()
    conn.close()
    return rows

# --- Таблиця працівників ---
def get_all_workers():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM work").fetchall()
    conn.close()
    return rows

# 🔹 Для тесту (необов’язково)
if __name__ == "__main__":
    print("Dishes:", len(get_all_dishes()))
    print("Services:", len(get_all_services()))
    print("Workers:", len(get_all_workers()))
