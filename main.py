from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import jsonify
import traceback
from database import (
    get_all_dish, get_dish_by_id, get_all_work, get_all_feedback, get_all_accounts,
    add_dish, add_work, delete_dish, delete_accounts, get_db, add_account, add_feedback,
    close_db, init_db, add_favourite, get_all_favourites, add_order, get_all_orders,
    add_admin, get_admin_by_username, check_password_hash,
    get_account_by_email, get_account_by_id, update_account, update_dish,
    get_order_by_id, update_order_status,
    get_favourite_by_dish, delete_favourite_by_dish,
    update_account_profile, get_orders_by_phone
)

import json

app = Flask(__name__)
app.secret_key = 'dev-change-me-to-secure-key'
from datetime import timedelta
app.permanent_session_lifetime = timedelta(days=30)
# Session cookie settings to help persistence across reloads
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
# Ensure DB connection is closed after each request
app.teardown_appcontext(close_db)

# Initialize Swagger documentation (Flasgger)
try:
    from flasgger import Swagger
    Swagger(app)
except Exception:
    # flasgger may not be installed in the environment; continue without swagger
    pass

# Register versioned API blueprints
try:
    from api import api_v1_bp, api_v2_bp
    app.register_blueprint(api_v1_bp)
    app.register_blueprint(api_v2_bp)
except Exception:
    # If import fails (e.g. missing dependencies), fallback to previous api if present
    try:
        from api import api_bp
        app.register_blueprint(api_bp)
    except Exception:
        pass


# Initialize DB and create a default admin once before handling requests
# Use before_request with a one-time flag for compatibility with older Flask
@app.before_request
def startup():
    if not app.config.get('DB_INIT_DONE'):
        try:
            with app.app_context():
                init_db()
                # Ensure default admin exists and set password to 11111
                add_admin('admin', '11111')
        except Exception:
            pass
        app.config['DB_INIT_DONE'] = True

# --- Головна сторінка ---
@app.route('/')
def index():
    dish = get_all_dish()
    return render_template('index.html', menu_items=dish)

# --- Сторінка окремої страви ---
@app.route('/dish/<int:dish_id>')
def dish(dish_id):
    dish = get_dish_by_id(dish_id)
    # determine if dish is in favourites
    user_id = session.get('user_id')
    fav = None
    is_fav = False
    if user_id:
        fav = get_favourite_by_dish(dish_id, user_id)
        is_fav = bool(fav)
    return render_template('dish.html', dish=dish, is_fav=is_fav)

# --- Сторінка "Про нас" ---
@app.route('/about')
def about():
    return render_template('about.html')

# --- Сторінка "Наші послуги" ---
@app.route('/service')
def service():
    return render_template('service.html')

# --- Сторінка "Наші локації" ---
@app.route('/locate')
def locate():
    return render_template('locate.html')

# --- Сторінка "Приєднуйся до нас" ---
@app.route('/work')
def work():
    work = get_all_work()
    return render_template('work.html', work=work)

# --- Сторінка "Замовлення" ---
@app.route('/order')
def order():
    # Show order creation UI and user's past orders (by phone) when available
    user_id = session.get('user_id')
    user_orders = []
    if user_id:
        acct = get_account_by_id(user_id)
        # sqlite3.Row doesn't implement .get(), use mapping access safely
        acct_phone = None
        if acct is not None:
            try:
                acct_phone = acct['phone']
            except Exception:
                acct_phone = None
        if acct_phone:
            raw_orders = get_orders_by_phone(acct_phone)
            # build items_text like admin view
            for o in raw_orders:
                items_text = ''
                try:
                    items = json.loads(o['items']) if 'items' in o.keys() else json.loads(o[4])
                except Exception:
                    items = []
                parts = []
                for it in items:
                    try:
                        # support multiple possible item formats
                        did = None
                        if isinstance(it, dict):
                            did = it.get('dish_id') or it.get('id') or it.get('dish')
                            qty = int(it.get('qty', 1))
                        else:
                            try:
                                if isinstance(it, (list, tuple)) and len(it) > 0:
                                    did = it[0]
                                    qty = int(it[1]) if len(it) > 1 else 1
                                else:
                                    did = int(it)
                                    qty = 1
                            except Exception:
                                did = None
                                qty = 1
                        try:
                            did_int = int(did)
                        except Exception:
                            did_int = None
                        if did_int is not None:
                            d = get_dish_by_id(did_int)
                            name = d['name'] if d and 'name' in d.keys() else f"#{did_int}"
                        else:
                            name = str(did or '#')
                    except Exception:
                        name = f"#{it}"
                        qty = 1
                    parts.append(f"{name} x{qty}")
                items_text = ', '.join(parts)
                od = dict(o)
                od['items_text'] = items_text
                user_orders.append(od)
    # pass dish list so order page can show a picker and prices
    dishes = get_all_dish()
    # allow preselecting a dish via query params
    pre_dish = request.args.get('dish_id')
    pre_qty = request.args.get('qty')
    account = None
    if user_id:
        account = get_account_by_id(user_id)
    return render_template('order.html', orders=user_orders, dishes=dishes, pre_dish=pre_dish, pre_qty=pre_qty, account=account)

# --- Сторінка "Улюблені страви" ---
# (Route implemented further down with DB-backed favourites)

# --- Сторінка "Адмін" ---
@app.route('/admin')
def admin():
    # Require admin login
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))

    dish = get_all_dish()
    feedback = get_all_feedback()
    work = get_all_work()
    orders = get_all_orders()
    # Build a human-readable items text for each order (dish names)
    orders_display = []
    for o in orders:
        items_text = ''
        try:
            items = json.loads(o['items']) if 'items' in o.keys() else json.loads(o[4])
        except Exception:
            items = []
        parts = []
        for it in items:
            try:
                # support multiple possible item formats
                did = None
                if isinstance(it, dict):
                    did = it.get('dish_id') or it.get('id') or it.get('dish')
                    qty = int(it.get('qty', 1))
                else:
                    # could be a plain id or [id,qty]
                    try:
                        if isinstance(it, (list, tuple)) and len(it) > 0:
                            did = it[0]
                            qty = int(it[1]) if len(it) > 1 else 1
                        else:
                            did = int(it)
                            qty = 1
                    except Exception:
                        did = None
                        qty = 1
                # coerce to int when possible
                try:
                    did_int = int(did)
                except Exception:
                    did_int = None
                if did_int is not None:
                    d = get_dish_by_id(did_int)
                    name = d['name'] if d and 'name' in d.keys() else f"#{did_int}"
                else:
                    name = str(did or '#')
            except Exception:
                name = f"#{it}"
                qty = 1
            parts.append(f"{name} x{qty}")
        items_text = ', '.join(parts)
        # copy row into dict-like object: convert sqlite Row to dict
        od = dict(o)
        od['items_text'] = items_text
        orders_display.append(od)
    accounts = get_all_accounts()
    return render_template('admin.html', dish=dish, work=work, feedback=feedback, orders=orders_display, accounts=accounts)


@app.route('/admin/dish/edit/<int:dish_id>', methods=['GET', 'POST'])
def admin_edit_dish(dish_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    dish = get_dish_by_id(dish_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        price = float(request.form.get('price', 0) or 0)
        image = request.form.get('image', '')
        description = request.form.get('description', '')
        ingredients = request.form.get('ingredients', '')
        calories = request.form.get('calories', '')
        update_dish(dish_id, name, price, image, description, ingredients, calories)
        flash('Страву оновлено', 'success')
        return redirect(url_for('admin'))
    return render_template('admin_edit_dish.html', dish=dish)


@app.route('/admin/accounts/edit/<int:account_id>', methods=['GET', 'POST'])
def admin_edit_account(account_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    account = get_account_by_id(account_id)
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        update_account(account_id, first_name, last_name, phone, email)
        flash('Акаунт оновлено', 'success')
        return redirect(url_for('admin'))
    return render_template('admin_edit_account.html', account=account)


@app.route('/admin/order/<int:order_id>/status', methods=['POST'])
def admin_update_order_status(order_id):
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    status = request.form.get('status', '').strip()
    if status:
        update_order_status(order_id, status)
        flash('Статус замовлення оновлено', 'success')
    return redirect(url_for('admin'))

# --- Сторінка "Акаунт" ---
@app.route('/account')
def account():
    user_id = session.get('user_id')
    account = None
    favourites = []
    user_orders = []
    if user_id:
        account = get_account_by_id(user_id)
        favourites = get_all_favourites(user_id)
        acct_phone = None
        if account is not None:
            try:
                acct_phone = account['phone']
            except Exception:
                acct_phone = None
        if acct_phone:
            raw_orders = get_orders_by_phone(acct_phone)
            # Convert orders rows to dicts with human-readable items_text
            for o in raw_orders:
                items_text = ''
                try:
                    items = json.loads(o['items']) if 'items' in o.keys() else json.loads(o[4])
                except Exception:
                    items = []
                parts = []
                for it in items:
                    try:
                        did = None
                        if isinstance(it, dict):
                            did = it.get('dish_id') or it.get('id') or it.get('dish')
                            qty = int(it.get('qty', 1))
                        else:
                            try:
                                if isinstance(it, (list, tuple)) and len(it) > 0:
                                    did = it[0]
                                    qty = int(it[1]) if len(it) > 1 else 1
                                else:
                                    did = int(it)
                                    qty = 1
                            except Exception:
                                did = None
                                qty = 1
                        try:
                            did_int = int(did)
                        except Exception:
                            did_int = None
                        if did_int is not None:
                            d = get_dish_by_id(did_int)
                            name = d['name'] if d and 'name' in d.keys() else f"#{did_int}"
                        else:
                            name = str(did or '#')
                    except Exception:
                        name = f"#{it}"
                        qty = 1
                    parts.append(f"{name} x{qty}")
                items_text = ', '.join(parts)
                od = dict(o)
                od['items_text'] = items_text
                user_orders.append(od)
    else:
        account = None
    return render_template('account.html', account=account, favourites=favourites, orders=user_orders)


@app.route('/account/edit', methods=['GET', 'POST'])
def account_edit():
    user_id = session.get('user_id')
    if not user_id:
        flash('Будь ласка, увійдіть, щоб редагувати профіль', 'info')
        return redirect(url_for('signUp'))
    account = get_account_by_id(user_id)
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        avatar = request.form.get('avatar', '').strip()
        bio = request.form.get('bio', '').strip()
        try:
            update_account_profile(user_id, first_name, last_name, phone, email, avatar, bio)
            flash('Профіль оновлено', 'success')
            return redirect(url_for('account'))
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            flash(f'Помилка при оновленні профілю: {e}', 'error')
    return render_template('account_edit.html', account=account)

# --- Сторінка "Вхід" ---
@app.route('/signUp')
def signUp():
    return render_template('signUp.html')


@app.route('/signUp/login', methods=['POST'])
def sign_up_login():
    # create or fetch account, then set session and redirect to account page
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    # password is not used for now, just accept registration
    password = request.form.get('password', '').strip()

    existing = get_account_by_email(email)
    if existing:
        account_id = existing['id']
    else:
        account_id = add_account(first_name, last_name, phone, email)
    session['user_id'] = account_id
    # Keep user logged in across browser sessions
    session.permanent = True
    flash('Ласкаво просимо!', 'success')
    return redirect(url_for('account'))

# --- Маршрути для додавання даних ---
@app.route('/admin/add_dish', methods=['GET', 'POST'])
def add_dish_route():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        image = request.form.get('image', '')
        description = request.form['description']
        ingredients = request.form['ingredients']
        calories = request.form['calories']
        
        try:
            add_dish(name, price, image, description, ingredients, calories)
            flash('Страву успішно додано!', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')
    
    return render_template('add_dish.html')

@app.route('/contact/add_feedback', methods=['GET', 'POST'])
def add_feedback_route():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        text = request.form.get('text', '').strip()
        try:
            add_feedback(name, email, text)
            flash('Ваш запит надіслано!', 'success')
            return redirect(url_for('index') + '#contact')
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')

    # On GET redirect to contact section of index
    return redirect(url_for('index') + '#contact')

@app.route('/work/add_work', methods=['GET', 'POST'])
def add_work_route():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form.get('phone', '')
        email = request.form['email']
        profecy = request.form['profecy']
        
        try:
            add_work(name, phone, email, profecy)
            flash("Ваша заявка прийнята! Очікуйте, ми з вами зв'яжемося", 'success')
            # After submitting the work application we should stay on the work page
            # and show a confirmation message rather than redirecting to the admin panel.
            return redirect(url_for('work') + '#forma')
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')
    
    work = get_all_work()
    return render_template('work.html', work=work)

@app.route('/signUp/add_accounts', methods=['GET', 'POST'])
def add_accounts_route():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        try:
            account_id = add_account(first_name, last_name, phone, email)
            # Log the user in immediately and make the session persistent
            session['user_id'] = account_id
            session.permanent = True
            flash("Акаунт створено", 'success')
            return redirect(url_for('account'))
        except Exception as e:
            flash(f'Помилка: {str(e)}', 'error')

    work = get_all_work()
    return render_template('work.html', work=work)

# --- Маршрути для видалення ---
@app.route('/admin/delete_dish/<int:dish_id>', methods=['POST'])
def delete_dish_route(dish_id):
    try:
        delete_dish(dish_id)
        flash('Страву успішно видалено!', 'success')
    except Exception as e:
        flash(f'Помилка: {str(e)}', 'error')
    return redirect(url_for('admin'))

@app.route('/admin/delete_accounts/<int:service_id>', methods=['POST'])
def delete_accounts_route(service_id):
    try:
        delete_accounts(service_id)
        flash('Акаунт успішно видалено!', 'success')
    except Exception as e:
        flash(f'Помилка: {str(e)}', 'error')
    return redirect(url_for('admin'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Ви вийшли з акаунту', 'info')
    return redirect(url_for('index'))


@app.route('/admin/reset-password', methods=['POST'])
def admin_reset_password():
    # Dev-only endpoint: reset admin password to 11111 when in debug mode
    if not app.debug:
        return ('Not allowed', 403)
    try:
        add_admin('admin', '11111')
        return ('OK', 200)
    except Exception as e:
        return (str(e), 500)


@app.route('/_debug_session')
def _debug_session():
    # Debug helper: returns session contents only when app.debug is True
    if not app.debug:
        return ('Not allowed', 403)
    try:
        return jsonify({k: session.get(k) for k in session.keys()})
    except Exception as e:
        return (str(e), 500)


# --- Favorites ---
@app.route('/favourite')
def favourite():
    user_id = session.get('user_id')
    if not user_id:
        flash('Щоб переглядати улюблені, увійдіть або зареєструйтесь', 'info')
        return redirect(url_for('signUp'))
    favs = get_all_favourites(user_id)
    return render_template('favourite.html', favourites=favs)


@app.route('/favourite/add/<int:dish_id>', methods=['POST'])
def add_to_favourite(dish_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Тільки зареєстровані користувачі можуть додавати улюблені. Увійдіть або зареєструйтесь.', 'info')
        return redirect(url_for('signUp'))
    try:
        add_favourite(dish_id, user_id)
        flash('Додано до улюблених', 'success')
    except Exception as e:
        flash(f'Помилка: {e}', 'error')
    return redirect(request.referrer or url_for('index'))


@app.route('/favourite/remove/<int:dish_id>', methods=['POST'])
def remove_from_favourite(dish_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Тільки зареєстровані користувачі можуть видаляти улюблені. Увійдіть або зареєструйтесь.', 'info')
        return redirect(url_for('signUp'))
    try:
        delete_favourite_by_dish(dish_id, user_id)
        flash('Видалено з улюблених', 'success')
    except Exception as e:
        flash(f'Помилка: {e}', 'error')
    return redirect(request.referrer or url_for('favourite'))

# --- Orders ---
@app.route('/order/create', methods=['POST'])
def create_order():
    try:
        name = request.form.get('name', '').strip() or 'Гість'
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        # Server-side validation: require table/address for dine-in orders
        if not address:
            flash('Будь ласка, вкажіть номер столу.', 'error')
            return redirect(url_for('order'))
        items_raw = request.form.get('items', '')
        items = []
        if items_raw:
            # items may be JSON or a CSV of ids
            try:
                parsed = json.loads(items_raw)
                if isinstance(parsed, list):
                    items = parsed
                else:
                    # fallback: wrap single item
                    items = [parsed]
            except Exception:
                # parse comma-separated ids
                items = [{'dish_id': int(x.strip()), 'qty': 1} for x in items_raw.split(',') if x.strip().isdigit()]
        else:
            dish_id = request.form.get('dish_id')
            if dish_id and str(dish_id).isdigit():
                items = [{'dish_id': int(dish_id), 'qty': int(request.form.get('qty', 1))}]

        total = 0.0
        db = get_db()
        cur = db.cursor()
        safe_items = []
        for raw in items:
            # normalize item to dict with dish_id and qty
            try:
                if isinstance(raw, dict):
                    did = int(raw.get('dish_id') or raw.get('id'))
                    qty = int(raw.get('qty', 1))
                elif isinstance(raw, (list, tuple)) and len(raw) > 0:
                    did = int(raw[0]); qty = int(raw[1]) if len(raw) > 1 else 1
                else:
                    # try treating as id
                    did = int(raw)
                    qty = 1
            except Exception:
                continue
            cur.execute('SELECT price FROM dish WHERE id = ?', (did,))
            row = cur.fetchone()
            price_f = 0.0
            if row:
                try:
                    price_val = row['price'] if 'price' in row.keys() else row[0]
                    price_f = float(price_val)
                except Exception:
                    price_f = 0.0
            total += price_f * qty
            safe_items.append({'dish_id': did, 'qty': qty})

        add_order(name, phone, address, safe_items, total)
        flash('Замовлення створено. Дякуємо!', 'success')
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        flash(f'Помилка при створенні замовлення: {e}', 'error')
    return redirect(url_for('order'))


# --- Admin login ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        admin = get_admin_by_username(username)
        if admin and check_password_hash(admin['password_hash'], password):
            session['is_admin'] = True
            session.permanent = True
            flash('Успішний вхід', 'success')
            return redirect(url_for('admin'))
        else:
            flash('Невірне ім’я користувача або пароль', 'error')
            return render_template('admin_login.html')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Ви вийшли', 'info')
    return redirect(url_for('index'))


# --- Запуск програми ---
if __name__ == '__main__':
    app.run(debug=True)
