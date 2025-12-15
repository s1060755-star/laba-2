"""
Security middleware and utilities for Flask application
"""
from functools import wraps
from flask import request, jsonify, session
import re
import html

def sanitize_html(text):
    """Очищення HTML для запобігання XSS атакам"""
    if not text:
        return ''
    # Екрануємо HTML символи
    return html.escape(str(text))

def validate_json_input(required_fields=None):
    """Декоратор для валідації JSON вхідних даних"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            if required_fields:
                missing = [field for field in required_fields if field not in data]
                if missing:
                    return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_auth(f):
    """Декоратор для перевірки авторизації користувача"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Декоратор для перевірки прав адміністратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def validate_sql_input(value):
    """Базова перевірка на SQL injection спроби"""
    if not value:
        return True
    
    dangerous_patterns = [
        r'(\bUNION\b.*\bSELECT\b)',
        r'(\bDROP\b.*\bTABLE\b)',
        r'(\bINSERT\b.*\bINTO\b)',
        r'(\bDELETE\b.*\bFROM\b)',
        r'(\bUPDATE\b.*\bSET\b)',
        r'(--)',
        r'(/\*|\*/)',
        r'(\bEXEC\b|\bEXECUTE\b)',
    ]
    
    value_upper = str(value).upper()
    for pattern in dangerous_patterns:
        if re.search(pattern, value_upper, re.IGNORECASE):
            return False
    
    return True

def secure_filename_custom(filename):
    """Безпечне ім'я файлу"""
    if not filename:
        return ''
    
    # Видаляємо шляхи
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Дозволяємо тільки безпечні символи
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Обмежуємо довжину
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:200] + ('.' + ext if ext else '')
    
    return filename

class SecurityHeaders:
    """Middleware для додавання security headers"""
    
    @staticmethod
    def add_csp_header(response):
        """Content Security Policy"""
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self';"
        )
        response.headers['Content-Security-Policy'] = csp
        return response
    
    @staticmethod
    def add_security_headers(response):
        """Додає всі необхідні security headers"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS для production
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response

def log_security_event(event_type, details):
    """Логування security подій"""
    from datetime import datetime
    timestamp = datetime.now().isoformat()
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    log_entry = f"[{timestamp}] {event_type} | IP: {ip} | UA: {user_agent} | {details}"
    
    # В production використовуйте proper logging
    print(f"SECURITY: {log_entry}")
    
    # Можна додати запис у файл або БД
    # with open('security.log', 'a') as f:
    #     f.write(log_entry + '\n')

def check_password_strength(password):
    """Перевірка міцності паролю"""
    if len(password) < 8:
        return False, "Пароль повинен містити мінімум 8 символів"
    
    if not re.search(r'[A-Z]', password):
        return False, "Пароль повинен містити хоча б одну велику літеру"
    
    if not re.search(r'[a-z]', password):
        return False, "Пароль повинен містити хоча б одну малу літеру"
    
    if not re.search(r'[0-9]', password):
        return False, "Пароль повинен містити хоча б одну цифру"
    
    return True, "Пароль відповідає вимогам"
