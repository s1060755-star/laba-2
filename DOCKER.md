# Docker / Compose — інструкція

Коротко: цей документ пояснює, як будувати і запускати контейнер з вашим Flask-застосунком та як працює збереження SQLite.

Створено/оновлено файли:
- `Dockerfile` — оптимізований образ на `python:3.13-slim`, non-root user, image-level `HEALTHCHECK`.
- `docker-compose.yml` — сервіс `web`, порти, environment, named volume `db_data` для збереження SQLite.

Як збирати та запускати

1) Побудувати образ вручну:

```powershell
docker build -t laba-2-web:latest .
```

2) Запустити з `docker-compose` (рекомендується):

```powershell
docker compose up -d --build
```

3) Переглянути логи:

```powershell
docker compose logs -f
```

4) Зупинити та видалити контейнери (зберігається volume):

```powershell
docker compose down
```

Де знаходиться база даних
- У контейнері шлях за замовчуванням: `/data/my_database.db`.
- На хості дані зберігаються у Docker named volume `db_data` (не в папці проєкту). Щоб тимчасово побачити файл на хості можна створити тимчасовий контейнер і промонтувати volume:

```powershell
docker run --rm -it -v laba-2_db_data:/data alpine ls -l /data
```

Змінні середовища
- `FLASK_SECRET` — секрет сесій (поставте у `.env` або середовищі CI).
- `FLASK_ENV` — `production` або `development`.
- `FLASK_DEBUG` — `0` або `1`.
- `DATABASE_PATH` — шлях до файлу БД (за замовчуванням `/data/my_database.db`).

Healthcheck
- Image-level `HEALTHCHECK` доступний та перевіряє `http://localhost:5000/health`.
- `docker-compose.yml` також містить `healthcheck`.

Рекомендації для продакшну
- Забезпечити секрети через Docker secrets або змінні середовища, не зберігати секрети в коді.
- За потреби змінити `gunicorn` workers відповідно до CPU.
- Розглянути використання окремого обробника статики, reverse proxy (nginx) для TLS/сертифікатів.

Project inventory — що є та чого нема

- **Наявне:**
  - `main.py` — Flask app з багатьма роутами та `/health` endpoint.
  - `database.py` — SQLite wrapper, `init_db()` створює таблиці; використовує `DATABASE_PATH` з env.
  - `requirements.txt` — перелік пакетів (`Flask`, `flasgger`, `gunicorn`).
  - `Dockerfile` — (оновлено) для запуску через `gunicorn`.
  - `docker-compose.yml` — (оновлено) сервіс `web` і named volume `db_data`.
  - `.dockerignore` — виключає `data/`, кеші, віртуальні оточення.
  - `templates/`, `static/` — фронтенд шаблони та ресурси.

- **Відсутнє / варто додати:**
  - `requirements.txt` з конкретними зафіксованими версіями (pinning) для відтворюваності.
  - `.env.example` для прикладу необхідних змінних середовища.
  - Тести/CI конфігурація (наприклад GitHub Actions) для автотестів і CI build.
  - Файл `gunicorn` config або supervisord, якщо потрібна тонка конфігурація воркерів.
  - Backup/restore інструкції для SQLite volume (якщо потрібен процес бекапу).
  - HTTPS/Reverse proxy приклад (nginx) для продакшн-розгортання.

Якщо хочете, можу додати:
- `.env.example` та зразок `.env` у `.gitignore`.
- Скрипт для бекапу файлу БД з volume на хості.
- GitHub Actions workflow для побудови образа та запуску простих тестів.

Автор: оновлено автоматично через скрипт. Якщо потрібен переклад або додаткові зміни — скажіть.
