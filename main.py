from flask import Flask, render_template
from database import get_all_dishes, get_dish_by_id, get_all_services, get_all_workers

app = Flask(__name__)

# --- Головна сторінка ---
@app.route('/')
def index():
    dishes = get_all_dishes()
    return render_template('index.html', menu_items=dishes)

# --- Сторінка окремої страви ---
@app.route('/dish/<int:dish_id>')
def dish(dish_id):
    dish = get_dish_by_id(dish_id)
    return render_template('dish.html', dish=dish)

# --- Сторінка "Про нас" ---
@app.route('/about')
def about():
    return render_template('about.html')

# --- Сторінка "Наші послуги" ---
@app.route('/service')
def service():
    services = get_all_services()
    return render_template('service.html', services=services)

# --- Сторінка "Наші локації" ---
@app.route('/locate')
def locate():
    return render_template('locate.html')

# --- Сторінка "Приєднуйся до нас" ---
@app.route('/work')
def work():
    workers = get_all_workers()
    return render_template('work.html', workers=workers)

# --- Сторінка "Замовлення" ---
@app.route('/order')
def order():
    return render_template('order.html')

# --- Сторінка "Улюблені страви" ---
@app.route('/favourite')
def favourite():
    return render_template('favourite.html')

# --- Сторінка "Адмін" ---
@app.route('/admin')
def admin():
    return render_template('admin.html')

# --- Сторінка "Акаунт" ---
@app.route('/account')
def account():
    return render_template('account.html')

# --- Сторінка "Вхід" ---
@app.route('/signUp')
def signUp():
    return render_template('signUp.html')

# --- Запуск програми ---
if __name__ == '__main__':
    app.run(debug=True)
