from flask import Flask, render_template, request, redirect, url_for, flash, session
from database import (
    get_all_dish, get_dish_by_id, get_all_work, get_all_feedback, get_all_accounts,
    add_dish, add_work, delete_dish, delete_accounts, get_db, add_account, add_feedback,
    close_db, init_db, add_favourite, get_all_favourites, add_order, get_all_orders,
    add_admin, get_admin_by_username, check_password_hash,
    get_account_by_email, get_account_by_id, update_account, update_dish,
    get_order_by_id, update_order_status
    , get_favourite_by_dish, delete_favourite_by_dish
)

import json

app = Flask(__name__)
app.secret_key = 'dev-change-me-to-secure-key'
# Ensure DB connection is closed after each request
app.teardown_appcontext(close_db)


# Initialize DB and create a default admin once before handling requests
# Use before_request with a one-time flag for compatibility with older Flask
@app.before_request
def startup():
    if not app.config.get('DB_INIT_DONE'):
        try:
            with app.app_context():
                init_db()
                add_admin('admin', 'admin')
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
    fav = get_favourite_by_dish(dish_id)
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
    return render_template('order.html')

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
    accounts = get_all_accounts()
    return render_template('admin.html', dish=dish, work=work, feedback=feedback, order=orders, accounts=accounts)


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
    if user_id:
        account = get_account_by_id(user_id)
    return render_template('account.html', account=account)

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
            add_account(first_name, last_name, phone, email)
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


# --- Favorites ---
@app.route('/favourite')
def favourite():
    favs = get_all_favourites()
    return render_template('favourite.html', favourites=favs)


@app.route('/favourite/add/<int:dish_id>', methods=['POST'])
def add_to_favourite(dish_id):
    try:
        add_favourite(dish_id)
        flash('Додано до улюблених', 'success')
    except Exception as e:
        flash(f'Помилка: {e}', 'error')
    return redirect(request.referrer or url_for('index'))


@app.route('/favourite/remove/<int:dish_id>', methods=['POST'])
def remove_from_favourite(dish_id):
    try:
        delete_favourite_by_dish(dish_id)
        flash('Видалено з улюблених', 'success')
    except Exception as e:
        flash(f'Помилка: {e}', 'error')
    return redirect(request.referrer or url_for('favourite'))

# --- Orders ---
@app.route('/order/create', methods=['POST'])
def create_order():
    name = request.form.get('name', '').strip() or 'Гість'
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()
    items_raw = request.form.get('items', '')
    if items_raw:
        try:
            items = json.loads(items_raw)
        except Exception:
            items = [{'dish_id': int(x.strip()), 'qty': 1} for x in items_raw.split(',') if x.strip().isdigit()]
    else:
        dish_id = request.form.get('dish_id')
        items = []
        if dish_id and dish_id.isdigit():
            items = [{'dish_id': int(dish_id), 'qty': int(request.form.get('qty', 1))}]

    total = 0.0
    db = get_db()
    cur = db.cursor()
    for it in items:
        cur.execute('SELECT price FROM dish WHERE id = ?', (it['dish_id'],))
        row = cur.fetchone()
        if row:
            total += (row['price'] if 'price' in row.keys() else row[0]) * it.get('qty', 1)

    try:
        add_order(name, phone, address, items, total)
        flash('Замовлення створено. Дякуємо!', 'success')
    except Exception as e:
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
