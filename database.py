import sqlite3
import os
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
import re

# --- Валідація даних ---
def validate_email(email):
    """Валідація email адреси"""
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Валідація телефонного номера"""
    if not phone or not isinstance(phone, str):
        return False
    # Видаляємо всі символи крім цифр та +
    cleaned = re.sub(r'[^\d+]', '', phone)
    # Перевірка довжини (мінімум 10 цифр)
    return len(re.sub(r'[^\d]', '', cleaned)) >= 10

def sanitize_string(value, max_length=500):
    """Очищення та обмеження довжини рядка"""
    if not value:
        return ''
    value = str(value).strip()
    # Видалення потенційно небезпечних символів
    value = re.sub(r'[<>]', '', value)
    return value[:max_length]

def validate_price(price):
    """Валідація ціни"""
    try:
        price_float = float(price)
        return 0 <= price_float <= 999999.99
    except (ValueError, TypeError):
        return False

def validate_integer(value, min_val=0, max_val=999999):
    """Валідація цілого числа"""
    try:
        int_val = int(value)
        return min_val <= int_val <= max_val
    except (ValueError, TypeError):
        return False


def get_db():
    """Підключення до бази даних з оптимізацією продуктивності"""
    if 'db' not in g:
        db_path = os.environ.get('DATABASE_PATH', 'my_database.db')
        # Ensure directory exists for file path
        try:
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        except Exception:
            pass
        g.db = sqlite3.connect(
            db_path,
            timeout=20.0,  # Збільшений timeout для concurrent requests
            check_same_thread=False
        )
        g.db.row_factory = sqlite3.Row  # Для отримання результатів у вигляді словника
        
        # Оптимізації SQLite для продуктивності
        cursor = g.db.cursor()
        cursor.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging для кращої concurrency
        cursor.execute('PRAGMA synchronous=NORMAL')  # Баланс між швидкістю та безпекою
        cursor.execute('PRAGMA cache_size=10000')  # Збільшений кеш (10MB)
        cursor.execute('PRAGMA temp_store=MEMORY')  # Тимчасові таблиці в пам'яті
        cursor.execute('PRAGMA mmap_size=268435456')  # Memory-mapped I/O (256MB)
        
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


def get_all_favourites(account_id=None):
    db = get_db()
    cursor = db.cursor()
    if account_id is None:
        cursor.execute('SELECT f.id, f.dish_id, d.name, d.price, d.image, f.account_id FROM favourites f LEFT JOIN dish d ON f.dish_id = d.id')
    else:
        cursor.execute('SELECT f.id, f.dish_id, d.name, d.price, d.image FROM favourites f LEFT JOIN dish d ON f.dish_id = d.id WHERE f.account_id = ?', (account_id,))
    favs = cursor.fetchall()
    return favs


def get_favourite_by_dish(dish_id, account_id=None):
    db = get_db()
    cursor = db.cursor()
    if account_id is None:
        cursor.execute('SELECT * FROM favourites WHERE dish_id = ? LIMIT 1', (dish_id,))
    else:
        cursor.execute('SELECT * FROM favourites WHERE dish_id = ? AND account_id = ? LIMIT 1', (dish_id, account_id))
    return cursor.fetchone()


def delete_favourite_by_dish(dish_id, account_id=None):
    db = get_db()
    cursor = db.cursor()
    if account_id is None:
        cursor.execute('DELETE FROM favourites WHERE dish_id = ?', (dish_id,))
    else:
        cursor.execute('DELETE FROM favourites WHERE dish_id = ? AND account_id = ?', (dish_id, account_id))
    db.commit()

def add_favourite(dish_id, account_id=None):
    db = get_db()
    cursor = db.cursor()
    if account_id is None:
        cursor.execute('INSERT INTO favourites (dish_id) VALUES (?)', (dish_id,))
    else:
        # avoid duplicate favourites for same user+dish
        cursor.execute('SELECT id FROM favourites WHERE dish_id = ? AND account_id = ?', (dish_id, account_id))
        if cursor.fetchone() is None:
            cursor.execute('INSERT INTO favourites (dish_id, account_id) VALUES (?, ?)', (dish_id, account_id))
    db.commit()
    return cursor.lastrowid

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
    # Створення індексів для оптимізації запитів
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dish_price ON dish(price)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dish_name ON dish(name)')
    
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
    # Індекси для швидкого пошуку замовлень
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_phone ON orders(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at DESC)')
    
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
            email TEXT,
            avatar TEXT DEFAULT '',
            bio TEXT DEFAULT ''
        )
    ''')
    # Індекс для швидкого пошуку по email (унікальність)
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_accounts_email ON accounts(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_accounts_phone ON accounts(phone)')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_id INTEGER,
            account_id INTEGER
        )
    ''')
    # Індекси для favourites (оптимізація запитів по користувачам та стравам)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_favourites_dish ON favourites(dish_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_favourites_account ON favourites(account_id)')
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_favourites_unique ON favourites(dish_id, account_id)')
    # If an older DB exists without account_id column, try to add it
    try:
        cursor.execute("ALTER TABLE favourites ADD COLUMN account_id INTEGER")
    except Exception:
        pass
    # Try to add avatar and bio columns to accounts in older DBs
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN avatar TEXT DEFAULT ''")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN bio TEXT DEFAULT ''")
    except Exception:
        pass
    # Ensure older DBs have 'phone' column on accounts and orders
    try:
        cursor.execute("ALTER TABLE accounts ADD COLUMN phone TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN phone TEXT")
    except Exception:
        pass
    # Ensure address/items/total/created_at/status exist on orders (no-op if already present)
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN address TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN items TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN total REAL")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN created_at TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN status TEXT")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE orders ADD COLUMN discount REAL")
    except Exception:
        pass
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    ''')
    # Індекс для швидкого пошуку адміністраторів
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_admin_username ON admin_accounts(username)')
    
    db.commit()
    try:
        cursor.execute("UPDATE dish SET image = CASE \
            WHEN image LIKE '/static/%' THEN substr(image, 9) \
            WHEN image LIKE 'static/%' THEN substr(image, 8) \
            ELSE image END")
    except Exception:
        pass
    db.commit()


# --- Функції для додавання даних ---
def add_dish(name, price, image, description, ingredients, calories):
    """Додавання страви з валідацією"""
    # Валідація
    name = sanitize_string(name, 200)
    if not name:
        raise ValueError("Назва страви не може бути порожньою")
    
    if not validate_price(price):
        raise ValueError("Некоректна ціна")
    
    image = sanitize_string(image, 500)
    description = sanitize_string(description, 2000)
    ingredients = sanitize_string(ingredients, 1000)
    
    if not validate_integer(calories, 0, 10000):
        raise ValueError("Некоректна кількість калорій")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO dish (name, price, image, description, ingredients, calories) VALUES (?, ?, ?, ?, ?, ?)',
        (name, float(price), image, description, ingredients, int(calories))
    )
    db.commit()
    return cursor.lastrowid

def add_work(name, phone, email, profecy):
    """Додавання заяви на роботу з валідацією"""
    name = sanitize_string(name, 200)
    if not name:
        raise ValueError("Ім'я не може бути порожнім")
    
    phone = sanitize_string(phone, 50)
    # Phone is optional for account creation here — do not enforce strict validation
    if not phone:
        phone = ''
    
    email = sanitize_string(email, 200)
    if not validate_email(email):
        raise ValueError("Некоректна email адреса")
    
    profecy = sanitize_string(profecy, 500)
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO work (name, phone, email, profecy) VALUES (?, ?, ?, ?)',
        (name, phone, email, profecy)
    )
    db.commit()
    return cursor.lastrowid

def add_feedback(name, email, text):
    """Додавання відгуку з валідацією"""
    name = sanitize_string(name, 200)
    if not name:
        raise ValueError("Ім'я не може бути порожнім")
    
    email = sanitize_string(email, 200)
    if not validate_email(email):
        raise ValueError("Некоректна email адреса")
    
    text = sanitize_string(text, 5000)
    if not text:
        raise ValueError("Текст відгуку не може бути порожнім")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO feedback (name, email, text) VALUES (?, ?, ?)',
        (name, email, text)
    )
    db.commit()
    return cursor.lastrowid

def add_account(first_name, last_name, phone, email):
    """Додавання акаунту з валідацією"""
    first_name = sanitize_string(first_name, 100)
    last_name = sanitize_string(last_name, 100)
    
    if not first_name or not last_name:
        raise ValueError("Ім'я та прізвище не можуть бути порожніми")
    
    phone = sanitize_string(phone, 50)
    # Debug: show phone value when validation fails
    try:
        print('DEBUG add_account phone:', repr(phone))
    except Exception:
        pass
    if not validate_phone(phone):
        raise ValueError("Некоректний телефонний номер")
    
    email = sanitize_string(email, 200)
    if not validate_email(email):
        raise ValueError("Некоректна email адреса")
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            'INSERT INTO accounts (first_name, last_name, phone, email, avatar, bio) VALUES (?, ?, ?, ?, ?, ?)',
            (first_name, last_name, phone, email, '', '')
        )
    except sqlite3.IntegrityError:
        raise ValueError("Акаунт з таким email вже існує")
    except Exception:
        cursor.execute(
            'INSERT INTO accounts (first_name, last_name, phone, email) VALUES (?, ?, ?, ?)',
            (first_name, last_name, phone, email)
        )
    db.commit()
    return cursor.lastrowid


def update_account_profile(account_id, first_name, last_name, phone, email, avatar='', bio=''):
    """Оновлення профілю акаунту з валідацією"""
    first_name = sanitize_string(first_name, 100)
    last_name = sanitize_string(last_name, 100)
    
    if not first_name or not last_name:
        raise ValueError("Ім'я та прізвище не можуть бути порожніми")
    
    phone = sanitize_string(phone, 50)
    if phone and not validate_phone(phone):
        raise ValueError("Некоректний телефонний номер")
    
    email = sanitize_string(email, 200)
    if not validate_email(email):
        raise ValueError("Некоректна email адреса")
    
    avatar = sanitize_string(avatar, 500)
    bio = sanitize_string(bio, 2000)
    
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('UPDATE accounts SET first_name = ?, last_name = ?, phone = ?, email = ?, avatar = ?, bio = ? WHERE id = ?',
                       (first_name, last_name, phone, email, avatar, bio, account_id))
    except Exception:
        cursor.execute('UPDATE accounts SET first_name = ?, last_name = ?, phone = ?, email = ? WHERE id = ?',
                       (first_name, last_name, phone, email, account_id))
    db.commit()


def get_orders_by_phone(phone):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM orders WHERE phone = ? ORDER BY created_at DESC', (phone,))
    return cursor.fetchall()



def add_order(customer_name, phone, address, items, total, discount=0.0):
    db = get_db()
    cursor = db.cursor()
    items_json = json.dumps(items)
    created = datetime.datetime.utcnow().isoformat()
    cursor.execute(
        'INSERT INTO orders (customer_name, phone, address, items, total, created_at, discount) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (customer_name, phone, address, items_json, total, created, float(discount or 0.0))
    )
    db.commit()
    return cursor.lastrowid


def add_admin(username, password):
    db = get_db()
    cursor = db.cursor()
    pw_hash = generate_password_hash(password)
    # If admin exists, update password. Otherwise insert.
    cursor.execute('SELECT id FROM admin_accounts WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE admin_accounts SET password_hash = ? WHERE username = ?', (pw_hash, username))
        db.commit()
        return row['id'] if 'id' in row.keys() else row[0]
    else:
        cursor.execute('INSERT INTO admin_accounts (username, password_hash) VALUES (?, ?)', (username, pw_hash))
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