# Лабораторна робота №5: Розробка RESTful API

## Інформація про проєкт
- **Назва проєкту:** [Velvet Bite]
- **Автори:** [Скоп`юк Олександра Іванівна, Зінькевич Олександра Василівна, Матяш Дарія Сергіївна]


## Опис проєкту
[API надають можливість взаємодії з інформацією про страви, замовлення, акаунти та обрані страви. Вони дозволяють отримувати списки та окремі елементи, створювати нові записи, оновлювати та видаляти існуючі, обробляють запити та відповіді у форматі JSON і повертають відповідні коди стану для коректної обробки помилок.]

## Технології
- Python 3.11
- Flask
- SQLite
- JavaScript
- Postman
- Flasgger
- Swagger

## Endpoints API

### 1. [Get All Dishes]
- **URL:** `/api/v2/dishes`
- **Метод:** `GET`
- **Опис:** [Показує всі страви]
- **Приклад запиту:**
```json
  GET "http://127.0.0.1:5000/api/v2/dishes"
```
- **Приклад відповіді:**
```json
  {
    "calories": 350,
    "description": "Спробуйте наш фірмовий десерт!",
    "id": 1,
    "image": "images/mini.jpg",
    "ingredients": "бісквіт, крем, цукор",
    "name": "Міні Червоний Оксамит",
    "price": "115.0"
  },
  {
    "calories": 200,
    "description": "Класичний лате з нотками вишні та легкою пінкою",
    "id": 2,
    "image": "images/latte.jpg",
    "ingredients": "кава, молоко, вишня ",
    "name": "Лате Velvet",
    "price": "65.0"
  },
  {
    "calories": 400,
    "description": "Домашній сирник з вершковим сиром",
    "id": 3,
    "image": "images/cheesecake.jpg",
    "ingredients": "біскрвіт, сирний крем, цукор ",
    "name": "Сирник класичний",
    "price": "70.0"
  }
```
- **Скріншот з Postman (або Swagger):**
![Get all dishes](ScreenshotsEndpoints/GetAllDishes.png)

### 2. [Get Dish by ID]
- **URL:** `/api/v2/dishes/1`
- **Метод:** `GET`
- **Опис:** [Надає інформацію про окрему страву за ID]
- **Приклад запиту:**
```json
  GET "http://127.0.0.1:5000/api/v2/dishes/3"
```
- **Приклад відповіді:**
```json
{
  {
  "calories": 400,
  "description": "Домашній сирник з вершковим сиром",
  "id": 3,
  "image": "images/cheesecake.jpg",
  "ingredients": "біскрвіт, сирний крем, цукор ",
  "name": "Сирник класичний",
  "price": "70.0"
}
}
```
- **Скріншот з Postman (або Swagger):**
![Get dish by ID](ScreenshotsEndpoints/GetDishByID.png)

### 3. [Create Dish]
- **URL:** `/api/v2/dishes`
- **Метод:** `POST`
- **Опис:** [Створює страву]
- **Приклад запиту:**
```json
{
  "name": "Test Soup",
  "price": 50.0,
  "image": "",
  "description": "Тестова страва",
  "ingredients": "вода, сіль",
  "calories": 120
}
```
- **Приклад відповіді:**
```json
{
  "id": 532
}
```
- **Скріншот з Postman (або Swagger):**
![Create dish](ScreenshotsEndpoints/CreateDish.png)

### 4. [Update Dish]
- **URL:** `/api/dishes/1`
- **Метод:** `PUT`
- **Опис:** [Оновлює страву]
- **Приклад запиту:**
```json
"name": "cake",
  "price": 60.0
```
- **Приклад відповіді:**
```json
{
    "calories": 80,
    "description": "Справжня класика кавового смаку",
    "id": 5,
    "image": "images/americano.jpg",
    "ingredients": "кава",
    "name": "Амерекано",
    "price": "55.0"
}
```
- **Скріншот з Postman (або Swagger):**
![Update Dish](ScreenshotsEndpoints/UpdateDish.png)

### 5. [Delete Dish]
- **URL:** `/api/dishes/1`
- **Метод:** `DELETE`
- **Опис:** [Видаляє страву]
- **Приклад запиту:**
```json
  DELETE "http://127.0.0.1:5000/api/v2/dishes/9"
```
- **Приклад відповіді:**
```json
{
  "ok": true
}
```
- **Скріншот з Postman (або Swagger):**
![Delete dish](ScreenshotsEndpoints/DeleteDish.png)

### 6. [Get Orders]
- **URL:** `/api/orders`
- **Метод:** `GET`
- **Опис:** [Надає інформацію про замовлення]
- **Приклад запиту:**
```json
  GET "http://127.0.0.1:5000/api/v2/orders"
```
- **Приклад відповіді:**
```json
 {
    "address": null,
    "created_at": "2025-11-13T13:10:16.662869",
    "customer_name": "Гість",
    "id": 1,
    "items": "[{\"dish_id\": 2, \"qty\": 1}]",
    "phone": null,
    "status": "completed",
    "total": 0
  },
  {
    "address": "Kyma 23",
    "created_at": "2025-11-13T16:17:24.413021",
    "customer_name": "Зінькевич Олександра",
    "id": 2,
    "items": "[{\"dish_id\": 2, \"qty\": 1}]",
    "phone": "0974612700",
    "status": "pending",
    "total": 0
  }
```
- **Скріншот з Postman (або Swagger):**
![Get Order](ScreenshotsEndpoints/GetOrder.png)

### 7. [Create Order]
- **URL:** `/api/orders`
- **Метод:** `POST`
- **Опис:** [Створює замовлення]
- **Приклад запиту:**
```json
{
  "name": "Test User",
  "phone": "380123456789",
  "address": "Test address",
  "items": [{"dish_id":1, "qty":1}]
}
```
- **Приклад відповіді:**
```json
{
  "id": 530,
  "total": 0
}
```
- **Скріншот з Postman (або Swagger):**
![Create order](ScreenshotsEndpoints/CreateOrder.png)

### 8. [Get Accounts]
- **URL:** `/api/accounts`
- **Метод:** `GET`
- **Опис:** [Показує всі аккаунти]
- **Приклад запиту:**
```json
  GET "http://127.0.0.1:5000/api/v2/accounts"
```
- **Приклад відповіді:**
```json
  {
    "avatar": "https://i.pinimg.com/736x/9b/b3/93/9bb39320b6e173fca583c4e8602473c3.jpg",
    "bio": "<3",
    "email": "s.zinkevych09@gmail.com",
    "first_name": "Зінькевич",
    "id": 1,
    "last_name": "Олександра",
    "phone": "0974612700"
  }
```
- **Скріншот з Postman (або Swagger):**
![Get accounts](ScreenshotsEndpoints/GetAccounts.png)

### 9. [Get Favourites for Account (example id=1)]
- **URL:** `/api/favourites/1`
- **Метод:** `GET`
- **Опис:** [Видає улюблені страви по ID аккаунта]
- **Приклад запиту:**
```json
  GET "http://127.0.0.1:5000/api/v2/favourites/1"
```
- **Приклад відповіді:**
```json
{
    "dish_id": 8,
    "id": 13,
    "image": "images/krembrule.jpg",
    "name": "Крем брюле",
    "price": "95.0"
  },
  {
    "dish_id": 1,
    "id": 14,
    "image": "images/mini.jpg",
    "name": "Міні Червоний Оксамит",
    "price": "115.0"
  }
```
- **Скріншот з Postman (або Swagger):**
![Get favorites for account](ScreenshotsEndpoints/GetFavoritesForAccount.png)

## Результати тестування в Postman (або Swagger)

### Тестовий сценарій 1: [Get All Dishes]
- **Мета:** [Перевірити, що API повертає список всіх страв у форматі JSON зі статусом 200.]
- **Результат:** ✅ Успішно
- **Скріншот:**
![Тест 1](ScreenshotsTesting/testingGetAllDishes.png)

### Тестовий сценарій 2: [Get Dish by ID]
- **Мета:** [Перевірити, що API повертає конкретну страву за ID]
- **Результат:** ✅ Успішно 
- **Скріншот:**
![Тест 2](ScreenshotsTesting/testingGetDishByID.png)

### Тестовий сценарій 3: [Create Dish]
- **Мета:** [Перевірити, що API дозволяє створити нову страву з коректними даними.]
- **Результат:** ✅ Успішно 
- **Скріншот:**
![Тест 3](Screenshotstesting/testingCreateDish.png)

### Тестовий сценарій 4: [Update Dish]
- **Мета:** [Перевірити, що API дозволяє оновити існуючу страву]
- **Результат:** ✅ Успішно 
- **Скріншот:**
![Тест 4](ScreenshotsTesting/testingUpdateDish.png)

### Тестовий сценарій 5: [Delete Dish]
- **Мета:** [Перевірити, що API дозволяє видалити страву]
- **Результат:** ✅ Успішно 
- **Скріншот:**
![Тест 5](ScreenshotsTesting/testingDeleteDish.png)

### Тестовий сценарій 6: [Get Orders]
- **Мета:** [Перевірити, що API повертає список всіх замовлень у форматі JSON зі статусом 200.]
- **Результат:** ✅ Успішно 
- **Скріншот:**
![Тест 6](ScreenshotsTesting/testingGetOrders.png)

### Тестовий сценарій 7: [Create Order]
- **Мета:** Перевірити, що API дозволяє створити нове замовлення з коректними даними.]
- **Результат:** ✅ Успішно 
- **Скріншот:**
![Тест 7](ScreenshotsTesting/testingCreateOrder.png)

### Тестовий сценарій 8: [Get Accounts]
- **Мета:** [Перевірити, що API повертає список всіх акаунтів у форматі JSON зі статусом 200.]
- **Результат:** ✅ Успішно 
- **Скріншот:**
![Тест 8](ScreenshotsTesting/testingGetAccounts.png)

### Тестовий сценарій 9: [Get Favourites for Account]
- **Мета:** [Перевірити, що API повертає список обраних страв для конкретного акаунта]
- **Результат:** ✅ Успішно 
- **Скріншот:**
![Тест 9](ScreenshotsTesting/testingGetFavourites.png)

## Обробка помилок
Список реалізованих кодів помилок:
- `400 Bad Request` - [валідація/помилки запиту]
- `404 Not Found` - [коли ресурс не знайдено]
- `500 Internal Server Error` - [неочікувана помилка на сервері]
- `403 Forbidden` - [коли користувач не має прав доступу до ресурсу]