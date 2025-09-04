# Проект «Гурман» (Gourmand)

Современное Django‑приложение для каталога мест, событий и отзывов с личными кабинетами пользователей, SEO (sitemap), формами аутентификации и управлением контентом через админ‑панель.

## Возможности
- **Публичные страницы**: главная, контакты, список и детали мест (`/places/`, `/place/<slug>/`), событий (`/events/`, `/event/<slug>/`), обзоры/отзывы (`/reviews/`, `/reviews/<slug>/`).
- **Профили**: регистрация, вход/выход, профиль и редактирование профиля (`/signup/`, `/signin/`, `/signout/`, `/profile/`, `/profile/edit/`).
- **Создание контента**: создание мест и событий, публикация отзывов, голосование за отзывы.
- **SEO**: карта сайта `sitemap.xml` для статических и динамических страниц.
- **Медиа и статика**: загрузка медиа, сбор и раздача статики.
- **Админ‑панель**: стандартная админка Django (`/admin/`).

## Технологический стек
- **Backend**: Django 5.x (проект `Gourmand`, приложение `landing`)
- **База данных**: SQLite (по умолчанию), легко заменить на PostgreSQL/MySQL
- **Статика**: `STATICFILES_DIRS = landing/static`, `STATIC_ROOT = staticfiles`
- **Медиа**: `MEDIA_ROOT = landing/media`, `MEDIA_URL = /media/`
- **Почта**: SMTP (Яндекс), готово к продакшен‑отправке писем
- **Кэш**: локальный (LocMemCache)
- **Прочее**: Python‑зависимости из `requirements.txt`, опционально Gunicorn + Nginx

## Структура
- `Gourmand/` — настройки проекта (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`)
- `landing/` — основное приложение (модели, формы, views, шаблонные теги, `urls.py`)
- `templates/` — шаблоны (auth, places, events, gourmands, includes и т.д.)
- `staticfiles/` — папка для собранной статики (`collectstatic`)
- `landing/static/` — исходники статики приложения
- `landing/media/` — медиа‑файлы (загрузка пользователями)

## Быстрый старт (локально)
Ниже пример для Windows PowerShell.

1) Клонировать и перейти в папку проекта:
```powershell
git clone <ВАШ_РЕПОЗИТОРИЙ>.git
cd Diploma
```

2) Создать и активировать виртуальное окружение:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3) Установить зависимости:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4) Создать файл `.env` в корне (рядом с `manage.py`) по примеру ниже.

5) Применить миграции и создать суперпользователя:
```powershell
python manage.py migrate
python manage.py createsuperuser
```

6) Собрать статику (по запросу подтвердите копирование):
```powershell
python manage.py collectstatic
```

7) Запустить сервер разработки:
```powershell
python manage.py runserver
```
Откройте `http://127.0.0.1:8000/`.

## Переменные окружения (.env)
Проект читает `.env` из корня через `python-dotenv`.
```dotenv
# Обязательные
SECRET_KEY=замените-на-секретный-ключ
DEBUG=True

# Email (Яндекс SMTP; для локальной отладки можете временно поставить консольный backend)
EMAIL_HOST_PASSWORD=пароль-приложения-яндекса

# Ключи капчи (если используются)
YANDEX_CAPTCHA_CLIENT_KEY=
YANDEX_CAPTCHA_SERVER_KEY=

# Интеграции (опционально)
OPENAI_API_KEY=
```
Замечания:
- Для продакшена установите `DEBUG=False`, заполните `ALLOWED_HOSTS` и `CSRF_TRUSTED_ORIGINS` в `Gourmand/settings.py`.
- В продакшене используйте почтовый бэкенд SMTP (настроен), в разработке можно временно использовать консольный backend.

## Основные URL
- Главная: `/`
- Аккаунт: `/signup/`, `/signin/`, `/signout/`, `/profile/`, `/profile/edit/`
- Места: `/places/`, `/place/<slug>/`, создание — `/places/create/`
- События: `/events/`, `/event/<slug>/`, создание — `/event/create/`
- Отзывы: `/reviews/`, `/reviews/<slug>/`, голосование — `/reviews/<slug>/vote/<vote_type>/`
- Карта сайта: `/sitemap.xml`
- Админка: `/admin/`

## Команды управления
```bash
python manage.py migrate            # миграции БД
python manage.py createsuperuser    # суперпользователь
python manage.py collectstatic      # сбор статики в ./staticfiles
python manage.py runserver          # запуск dev‑сервера
```

## Деплой (Gunicorn + Nginx)
Минимальный набросок для одного хоста со сбором статики и проксированием через Nginx.

1) Установить Gunicorn и запустить приложение:
```bash
gunicorn Gourmand.wsgi:application --bind 127.0.0.1:8000 --workers 3
```
Обычно оформляется через systemd‑юнит, чтобы процесс перезапускался автоматически.

2) Собрать статику и убедиться, что `STATIC_ROOT` и `MEDIA_ROOT` совпадают с настройками Nginx:
```bash
python manage.py collectstatic
```

3) Настроить Nginx. В репозитории есть пример `nginx_settings.txt` с HTTPS, редиректами и alias для статики/медиа. Важные моменты:
- `location /static/ { alias /path/to/project/staticfiles/; }`
- `location /media/ { alias /path/to/project/landing/media/; }`
- `location / { proxy_pass http://127.0.0.1:8000; }`
- Для HTTPS используйте сертификаты Let’s Encrypt; HSTS включайте после проверки.

4) Переменные окружения и секреты держите вне репозитория (например, в `/etc/environment`, systemd `EnvironmentFile`, `.env`).

## Замена БД (опционально)
Для PostgreSQL:
- Установите `psycopg` и пропишите в `DATABASES` параметры подключения.
- Выполните миграции, соберите статику.

## Отладка
- Логи пишутся в `debug.log` (см. `LOGGING` в `Gourmand/settings.py`).
- При ошибках со статикой проверьте, что `collectstatic` прошёл успешно и пути в Nginx соответствуют `STATIC_ROOT` и `MEDIA_ROOT`.

## Лицензия
Не указана. Добавьте файл `LICENSE`, если требуется. 