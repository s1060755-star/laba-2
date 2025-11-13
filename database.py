import sqlite3
from flask import g
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except Exception:
    # Provide a minimal fallback using hashlib.pbkdf2_hmac if werkzeug is not installed.
    import hashlib
    import os

    def generate_password_hash(password: str) -> str:
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
        return salt.hex() + ':' + dk.hex()

    def check_password_hash(pw_hash: str, password: str) -> bool:
        try:
            salt_hex, dk_hex = pw_hash.split(':', 1)
            salt = bytes.fromhex(salt_hex)
            dk = bytes.fromhex(dk_hex)
            new_dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
            return hashlib.compare_digest(new_dk, dk)
        except Exception:
            return False
import json
import datetime

def get_db():
    """Підключення до бази даних"""
    if 'db' not in g:
        g.db = sqlite3.connect('my_database.db')
        g.db.row_factory = sqlite3.Row  # Для отримання результатів у вигляді словника
    return g.db

def close_db(e=None):
    """Закриття з'єднання з БД"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Функції для отримання даних ---
def get_all_dish():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM dish')
    dish = cursor.fetchall()
    return dish

def get_all_orders():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    return orders
def get_all_work():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM work')
    work = cursor.fetchall()
    return work

def get_dish_by_id(dish_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM dish WHERE id = ?', (dish_id,))
    return cursor.fetchone()

def get_all_feedback():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM feedback')
    feedback = cursor.fetchall()
    return feedback

def get_all_accounts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM accounts')
    accounts = cursor.fetchall()
    return accounts


def get_all_favourites():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT f.id, f.dish_id, d.name, d.price, d.image FROM favourites f LEFT JOIN dish d ON f.dish_id = d.id')
    favs = cursor.fetchall()
    return favs


def get_favourite_by_dish(dish_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM favourites WHERE dish_id = ? LIMIT 1', (dish_id,))
    return cursor.fetchone()


def delete_favourite_by_dish(dish_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM favourites WHERE dish_id = ?', (dish_id,))
    db.commit()

# --- Функції для ініціалізації/адміністрації ---
def init_db():
    db = get_db()
    cursor = db.cursor()
    # Create tables if they do not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dish (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            image TEXT,
            description TEXT,
            ingredients TEXT,
            calories INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS work (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            profecy TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            phone TEXT,
            address TEXT,
            items TEXT,
            total REAL,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            text TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_id INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    db.commit()


# --- Функції для додавання даних ---

# --- Функції для додавання даних ---
def add_dish(name, price, image, description, ingredients, calories):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO dish (name, price, image, description, ingredients, calories) VALUES (?, ?, ?, ?, ?, ?)',
        (name, price, image, description, ingredients, calories)
    )
    db.commit()
    return cursor.lastrowid

def add_work(name, phone, email, profecy):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO work (name, phone, email, profecy) VALUES (?, ?, ?, ?)',
        (name, phone, email, profecy)
    )
    db.commit()
    return cursor.lastrowid

def add_feedback(name, email, text):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO feedback (name, email, text) VALUES (?, ?, ?)',
        (name, email, text)
    )
    db.commit()
    return cursor.lastrowid

def add_account(first_name, last_name, phone, email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO accounts (first_name, last_name, phone, email) VALUES (?, ?, ?, ?)',
        (first_name, last_name, phone, email)
    )
    db.commit()
    return cursor.lastrowid


def add_favourite(dish_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO favourites (dish_id) VALUES (?)', (dish_id,))
    db.commit()
    return cursor.lastrowid


def add_order(customer_name, phone, address, items, total):
    db = get_db()
    cursor = db.cursor()
    items_json = json.dumps(items)
    created = datetime.datetime.utcnow().isoformat()
    cursor.execute(
        'INSERT INTO orders (customer_name, phone, address, items, total, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        (customer_name, phone, address, items_json, total, created)
    )
    db.commit()
    return cursor.lastrowid


def add_admin(username, password):
    db = get_db()
    cursor = db.cursor()
    pw_hash = generate_password_hash(password)
    cursor.execute('INSERT OR IGNORE INTO admin_accounts (username, password_hash) VALUES (?, ?)', (username, pw_hash))
    db.commit()
    return cursor.lastrowid


def get_admin_by_username(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM admin_accounts WHERE username = ?', (username,))
    return cursor.fetchone()


def get_account_by_email(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM accounts WHERE email = ?', (email,))
    return cursor.fetchone()


def get_account_by_id(account_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM accounts WHERE id = ?', (account_id,))
    return cursor.fetchone()


def update_account(account_id, first_name, last_name, phone, email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE accounts SET first_name = ?, last_name = ?, phone = ?, email = ? WHERE id = ?',
                   (first_name, last_name, phone, email, account_id))
    db.commit()


def update_dish(dish_id, name, price, image, description, ingredients, calories):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        UPDATE dish SET name = ?, price = ?, image = ?, description = ?, ingredients = ?, calories = ?
        WHERE id = ?
    ''', (name, price, image, description, ingredients, calories, dish_id))
    db.commit()


def get_order_by_id(order_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    return cursor.fetchone()


def update_order_status(order_id, status):
    db = get_db()
    cursor = db.cursor()
    # ensure column exists — try adding if missing
    try:
        cursor.execute('ALTER TABLE orders ADD COLUMN status TEXT')
    except Exception:
        pass
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    db.commit()

# --- Функції для видалення даних ---
def delete_dish(dish_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM dish WHERE id = ?', (dish_id,))
    db.commit()

def delete_accounts(accounts_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM accounts WHERE id = ?', (accounts_id,))
    db.commit()