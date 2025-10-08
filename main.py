from flask import Flask, render_template

app = Flask(__name__)

# Дані меню 
menu_items = [
    {
        "id": 1,
        "name": "Міні Червоний Оксамит",
        "price": "95 грн",
        "image": "images/mini.jpg",
        "description": "Наш фірмовий десерт з ніжного червоного бісквіту та вершкового крему",
        "ingredients": ["бісквіт", "крем", "цукор"],
        "calories": 350
    },
    {
        "id": 2,
        "name": "Лате Velvet",
        "price": "65 грн",
        "image": "images/latte.jpg",
        "description": "Класичний лате з нотками вишні та легкою пінкою",
        "ingredients": ["бісквіт", "крем", "цукор"],
        "calories": 350
    },
    {
        "id": 3,
        "name": "Сирник з вишнею",
        "price": "80 грн",
        "image": "images/cheesecakechery.jpg",
        "description": "Домашній сирник з вишнею та карамельним соусом",
        "ingredients": ["бісквіт", "крем", "цукор"],
        "calories": 350
    },
    {
        "id": 4,
        "name": "Сирник класичний",
        "price": "70 грн",
        "image": "images/cheesecake.jpg",
        "description": "Домашній сирник з вершковим сиром",
        "ingredients": ["бісквіт", "крем", "цукор"],
        "calories": 350
    },
    {
        "id": 5,
        "name": "Капучино",
        "price": "65 грн",
        "image": "images/kapych.jpg",
        "description": "Ніжна кава з молочною піною",
        "ingredients": ["бісквіт", "крем", "цукор"],
        "calories": 350
    },
    {
        "id": 6,
        "name": "Американо",
        "price": "55 грн",
        "image": "images/americano.jpg",
        "description": "Справжня класика кавового смаку",
        "ingredients": ["бісквіт", "крем", "цукор"],
        "calories": 350
    }
]

# --- Головна сторінка ---
@app.route('/')
def index():
    return render_template('index.html', menu_items=menu_items)

# --- Сторінка окремої страви ---
@app.route('/dish/<int:dish_id>')
def dish(dish_id):
    dish = next((d for d in menu_items if d["id"] == dish_id), None)
    return render_template('dish.html', dish=dish)

# --- Сторінка "Про нас" ---
@app.route('/about')
def about():
    return render_template('about.html')

# --- Запуск програми ---
if __name__ == '__main__':
    app.run(debug=True)
