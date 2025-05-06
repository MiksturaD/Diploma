# Уже что-то похожее на взрослый деплой

## Шаг 0. Покупаем сервер, получаем ssh доступ
Ну взрослый уже должен с этим справиться.

И также изменяем ALLOWED_HOSTS

## Шаг 1. Подключаемся, создаем пользователя и устанавливаем всякие штуки
```bash
ssh username@your.server.ip
```

```bash
adduser mascap
```

Указываем пароль и данные.

Дадим пользователю права `sudo`

```bash
usermod -aG sudo mascap
```

Теперь переходим на нашего созданного пользователя:
```bash
su - mascap
```

Если только открыли консоль, то можно будет писать так:
```bash
ssh ssh mascap@212.192.217.30
```


Обновляем и ставим:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx git -y
```

## Шаг 2. Загружаем проект

```bash
cd ~
mkdir Diploma
cd Diploma
git clone https://github.com/MiksturaD/Diploma.git .
```

## Шаг 3. Виртуалка + зависимости

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Шаг 4. Настраиваем `.env`

Создаем файл `.env`
```bash
nano .env
```

В файл вставляем:
```ini
SECRET_KEY=<your-very-secret-key>
DEBUG=False
```

Потом поочереди комбинации клавиш:
1. `Ctrl + O`, `Enter` - это мы сохранили файл
2. `Ctrl + X` - вышли из изменения файла

## Шаг 5. Собираем и готовим проект

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

Дадим права `nginx` и другим пользователям, иначе статика будет недоступна:
```bash
sudo chmod o+x /home
sudo chmod o+x /home/mascap
sudo chmod o+x /home/mascap/Gourmand
sudo chmod -R o+rX /home/mascap/Gourmand/static
```

## Шаг 6. Пробуем `gunicorn`
```bash
gunicorn Gourmand.wsgi:application --bind 127.0.0.1:8000
```

Здесь `Gourmand` это папка где находиться `settings.py`

Если запустилось без ошибок — отлично. `Ctrl+C` чтобы выйти.


## Шаг 7. systemd юнит (сервис в Linux) для gunicorn

Создаём сервис:
```bash
sudo nano /etc/systemd/system/taskmanager.service
```

Вставь (замени `hugant` и `taskmanager`):
```ini
[Unit]
Description=Gunicorn for taskmanager
After=network.target

[Service]
User=mascap
Group=www-data
WorkingDirectory=/home/mascap/Gourmand
Environment="PATH=/home/mascap/Gourmand/venv/bin"
ExecStart=/home/mascap/Gourmand/venv/bin/gunicorn Gourmand.wsgi:application --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

И также `Ctrl + O`, `enter`, `Ctrl + X`.

Далее в консоле, запускаем этот сервис:

```bash
sudo systemctl daemon-reexec
sudo systemctl start Gourmand
sudo systemctl enable Gourmand
```

Проверяем:

```bash
systemctl status Gourmand
```

## Шаг 8. Настраиваем nginx

```bash
sudo nano /etc/nginx/sites-available/Gourmand
```

Пример, не забудь изменить `ip сервера` и `hugant`:
```nginx
server {
    listen 80;
    server_name 212.192.217.30;

    location /static/ {
        alias /home/mascap/Gourmand/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        include proxy_params;
    }
}
```

Подключаем сайт:
```bash
sudo ln -s /etc/nginx/sites-available/Gourmand /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```


## Должно работать

Если что-то изменили в коде, нужно перезапустить сервис
```bash
sudo systemctl restart taskmanager
```