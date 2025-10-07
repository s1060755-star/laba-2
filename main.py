from flask import Flask, render_template

app = Flask(__name__)

# --- Головна сторінка ---
@app.route('/')
def home():
    dishes = [
        {
            "name": "Міні Червоний Оксамит",
            "image": "images/red_velvet_mini.jpg",
            "description": "Ніжний десерт із вершковим кремом, натхненний класичним червоним велветом."
        },
        {
            "name": "Капкейк Velvet Kiss",
            "image": "images/banner1.jpg",
            "description": "М’який капкейк із червоного тіста та легким крем-сиром."
        }
    ]
    return render_template('index.html', dishes=dishes)


# --- Сторінка окремої страви ---
@app.route('/dish/<name>')
def dish(name):
    dishes = {
        "Міні Червоний Оксамит": {
            "image": "images/red_velvet_mini.jpg",
            "text": "Цей десерт має насичений смак какао з нотками ванілі та крем-сиром. Ідеальний до кави!"
        },
        "Капкейк Velvet Kiss": {
            "image": "images/banner1.jpg",
            "text": "Легкий капкейк із ніжним кремом та повітряною текстурою — смакує, як поцілунок!"
        }
    }
    dish_info = dishes.get(name, None)
    return render_template('dish.html', name=name, dish=dish_info)


# --- Сторінка "Про нас" ---
@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
