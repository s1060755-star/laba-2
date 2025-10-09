# laba-2
#  Velvet Bite

**Velvet Bite** 
Проєкт реалізує сайт кафе з меню десертів і кавових напоїв, де користувач може переглянути страви, отримати їхній опис, склад, калорійність та ціну. Сайт має окремі сторінки для кожної позиції, а також секцію “Про нас” і форму зворотного зв’язку.

---

## Мета роботи
Створення професійного робочого середовища для командної розробки програмного забезпечення,  
оволодіння основними принципами роботи з системою контролю версій **Git**  
та впровадження ефективного **Git workflow** для групової роботи над програмними проєктами.

---

## Опис проєкту

**Velvet Bite** — це динамічний сайт кафе, побудований на базі **Flask (Python)**,  
який відображає меню страв із серверних даних.  

Відвідувач може:
- ознайомитися з асортиментом десертів та кави;
- натиснути на страву, щоб переглянути детальний опис;
- переглянути інгредієнти, калорійність та вартість;
- скористатися формою для зв’язку з кафе.

---

## Основна функціональність

- **Головна сторінка** — коротке вітання та кнопка переходу до меню  
- **Меню** — перелік десертів і напоїв (зображення, опис, ціна)  
- **Сторінка окремої страви** — детальна інформація (опис, інгредієнти, калорійність, ціна)  
- **Контактна форма** — поля для введення імені, пошти та повідомлення  
- **Сторінка “Про нас”** — інформація про кафе  
- **Навігаційне меню** (“Головна”, “Меню”, “Контакти”, “Про нас”)  

---

## Використані технології

| Категорія | Технології |
|------------|-------------|
| **Мови розмітки та стилів** | HTML (43%), CSS (38.5%) |
| **Мова програмування** | Python (17.8%) |
| **Скрипти / інтерактивність** | JavaScript (0.7%) |
| **Фреймворк** | Flask |
| **Інструменти** | VS Code, Git, GitHub |
| **Контроль версій** | Git Workflow (branch → commit → pull request → merge) |

---
# Інсталяція та запуск: 
прописати команду cd document в Gitbush, далі відкрити GitHub, копіювати посилення репозиторію(https://github.com/s1060755-star/laba-2.git), в Gitbush прописати команду git clone посилання
## Структура репозиторію
laba-2/ 
│
├── static/
│   ├── images/
│   │   ├── americano.jpg
│   │   ├── banner3.jpg
│   │   ├── cheesecake.jpg
│   │   ├── cheesecakechery.jpg
│   │   ├── kapych.jpg
│   │   ├── latte.jpg
│   │   └── mini.jpg
│   │
│   ├── script.js
│   └── style.css
│
├── templates/
│   ├── about.html
│   ├── dish.html
│   └── index.html
│
├── .gitignore
├── main.py
└── README.md    
# Git Workflow команди
Для організації командної роботи над проєктом Velvet Bite використовувався Git та GitHub.
Команда дотримувалася базового Git Workflow для спільної розробки, який включав такі етапи:
1)Створення репозиторію
⦁	Репозиторій проєкту було створено на GitHub.
⦁	Учасники команди отримали доступ через collaborators
2)Клонування репозиторію - https://github.com/s1060755-star/laba-2.git
Кожен учасник працював із власною локальною копією проєкту у VS Code.
3)Робота в окремих гілках
⦁	Для кожної частини сайту створювалася окрема гілка:
git checkout -b feature/navbar
git checkout -b feature/menu
git checkout -b feature/contacts
Це дозволяло уникати конфліктів у коді.

4)Коміти 
git commit -m "Initial commit"
git commit -m "Inital commit:added base project files"
git commit -m "Update main.py"
git commit -m "feat: add test function hello in main.py"
git commit -m "Update main.py"
git commit -m "Merge branch 'main' into feature/navbar"
git commit -m "Merge pull request #1 from s1060755-star/feature/navbar"
git commit -m "chore: add base files for cafe website"
git commit -m "Update main.py"
git commit -m "Merge pull request #2 from s1060755-star/feature/menu"
git commit -m "Update main.py"
git commit -m "Merge branch 'main' into feature/contacts"
git commit -m "Merge pull request #3 from s1060755-star/feature/contacts"
git commit -m "Initial commit: index.html; style.css; script.js; main.py; images."
git commit -m "feat: add files"
git commit -m "feat: fiksyla faily"
git commit -m "feat: flask"
git commit -m "feat: fix site"
git commit -m "feat: update README.md, added CHANGLELOG.md, added laba-2-report.md"

5)Публікація змін на GitHub
git push origin feature/menu
git push origin main

6)Pull Request (PR)
Після завершення роботи над функціоналом учасник створював Pull Request для перевірки змін.
Інші члени команди могли переглянути код, залишити коментарі або запропонувати виправлення.

7)Злиття гілок і оновлення main
Після перевірки PR зміни об’єднувалися з головною гілкою main:
git checkout main
git pull origin main

8)Робота з конфліктами
Якщо виникали конфлікти, вони вирішувались безпосередньо у VS Code.
# Учасники команди 
⦁	Скоп`юк Олександра Іванівна, Team Leader (посилання на профіль GitHub - https://github.com/s1060755-star)
⦁	Зінькевич Олександра Василівна, Developer (посилання на профіль GitHub - https://github.com/szinkevych09-pixel)
⦁	Матяш Дарія Сергіївна, QA/Документатор (посилання на профіль GitHub - https://github.com/TuffDasha)

