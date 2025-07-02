#!/bin/bash

set -e

# Скрипт разворачивает Django-проект под Apache и mod_wsgi.
# Он старается не перезаписывать существующие файлы,
# поэтому подходит для донастройки уже созданного проекта.

echo "=== Django + Apache + mod_wsgi setup ==="

read -p "Введите имя проекта (например: mysite): " PROJECT_NAME
read -p "Введите имя приложения (например: app): " APP_NAME
read -p "Введите домен или IP для ALLOWED_HOSTS: " HOSTNAME
read -p "Каталог для проектов [/usr/share/django-projects]: " BASE_DIR
BASE_DIR=${BASE_DIR:-/usr/share/django-projects}
PROJECT_DIR="${BASE_DIR}/${PROJECT_NAME}"

echo "== Проверка окружения =="
echo "Проект: $PROJECT_NAME"
echo "Приложение: $APP_NAME"
echo "Хост: $HOSTNAME"
echo "Каталог проекта: $PROJECT_DIR"
ls -ld "$PROJECT_DIR" 2>/dev/null || echo "Каталог будет создан"
which python3
which apache2 2>/dev/null || which httpd

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Создаю директории..."
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown $USER:$USER "$PROJECT_DIR"
fi
cd "$PROJECT_DIR"
echo "Рабочая директория: $(pwd)"

if [ ! -d "venv" ]; then
    echo "Создаю виртуальное окружение..."
    python3 -m venv venv
fi
source venv/bin/activate

echo "Устанавливаю Django, gunicorn, matplotlib, mod_wsgi..."
pip install --upgrade django gunicorn matplotlib mod_wsgi

if [ ! -f "$PROJECT_NAME/manage.py" ] && [ ! -f "manage.py" ]; then
    echo "Создаю Django проект..."
    django-admin startproject "$PROJECT_NAME" .
    ls -d "$PROJECT_NAME"
fi

if [ ! -d "$APP_NAME" ]; then
    echo "Создаю приложение $APP_NAME..."
    python manage.py startapp "$APP_NAME"
    ls -d "$APP_NAME"
fi

if ! grep -q "'${APP_NAME}'" ${PROJECT_NAME}/settings.py; then
    echo "Добавляю $APP_NAME в settings.py..."
    sed -i "/INSTALLED_APPS = \[/ a\    '$APP_NAME'," ${PROJECT_NAME}/settings.py
fi

sed -i "s/ALLOWED_HOSTS = .*/ALLOWED_HOSTS = ['$HOSTNAME']/" ${PROJECT_NAME}/settings.py
sed -i "s/DEBUG = True/DEBUG = False/" ${PROJECT_NAME}/settings.py

if ! grep -q "STATIC_ROOT" ${PROJECT_NAME}/settings.py; then
    echo "Создаю статик и медиа директории..."
    mkdir -p static media
    echo -e "
STATIC_ROOT = BASE_DIR / 'static'
MEDIA_ROOT = BASE_DIR / 'media'
" >> ${PROJECT_NAME}/settings.py
    ls -d static media
fi

python manage.py migrate
python manage.py collectstatic --noinput

if ! grep -q "def plot_view" $APP_NAME/views.py 2>/dev/null; then
    echo "Создаю пример plot view..."
    cat > $APP_NAME/views.py <<'EOV'
from django.http import HttpResponse
import matplotlib.pyplot as plt
import io
import urllib, base64


def plot_view(request):
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3, 4], [10, 20, 25, 30])
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = 'data:image/png;base64,' + urllib.parse.quote(string)
    html = f'<img src="{uri}"/>'
    return HttpResponse(html)
EOV
fi

if [ ! -f "$APP_NAME/urls.py" ]; then
    echo "Создаю $APP_NAME/urls.py..."
    cat > $APP_NAME/urls.py <<'EOV'
from django.urls import path
from . import views

urlpatterns = [
    path('plot/', views.plot_view, name='plot'),
]
EOV
fi

if ! grep -q "include('$APP_NAME.urls')" ${PROJECT_NAME}/urls.py; then
    echo "Подключаю $APP_NAME.urls в ${PROJECT_NAME}/urls.py..."
    sed -i "s/from django.urls import path/from django.urls import path, include/" ${PROJECT_NAME}/urls.py
    sed -i "/urlpatterns = \[/ a\    path('', include('$APP_NAME.urls'))," ${PROJECT_NAME}/urls.py
fi

APACHE_SSL_CONF="/etc/apache2/sites-available/000-default-le-ssl.conf"
APACHE_HTTP_CONF="/etc/apache2/sites-available/000-default.conf"
echo "Настраиваю Apache..."

sudo bash -c "cat > $APACHE_SSL_CONF" <<EOV
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerAdmin kyamovvm@gmail.com
    ServerName $HOSTNAME
    ServerAlias www.$HOSTNAME
    DocumentRoot ${BASE_DIR}/

    ErrorLog \${APACHE_LOG_DIR}/error.log
    CustomLog \${APACHE_LOG_DIR}/access.log combined

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/$HOSTNAME/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/$HOSTNAME/privkey.pem


    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Permissions-Policy "geolocation=(), microphone()"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"

    WSGIDaemonProcess ${PROJECT_NAME} user=www-data group=www-data python-path=${PROJECT_DIR}
    WSGIProcessGroup ${PROJECT_NAME}
    WSGIScriptAlias / ${PROJECT_DIR}/${PROJECT_NAME}/wsgi.py

    <Directory ${PROJECT_DIR}/${PROJECT_NAME}>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    Alias /static/ ${PROJECT_DIR}/static/
    <Directory ${PROJECT_DIR}/static>
        Require all granted
    </Directory>
</VirtualHost>
</IfModule>
EOV

sudo bash -c "cat > $APACHE_HTTP_CONF" <<EOV
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    ServerName $HOSTNAME
    ServerAlias www.$HOSTNAME

    Redirect permanent / https://$HOSTNAME/
</VirtualHost>
EOV

sudo systemctl reload apache2

echo "Права на проект для www-data..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

# Вывод последних строк журнала ошибок Apache
LOG_FILE="${APACHE_LOG_DIR:-/var/log/apache2}/error.log"
if [ ! -f "$LOG_FILE" ]; then
    LOG_FILE="/var/log/httpd/error_log"
fi
echo "Последние сообщения из $LOG_FILE:"
sudo tail -n 20 "$LOG_FILE" | tee django_error_tail.log

echo "=== Готово! ==="
echo "Перейди в браузер на http://$HOSTNAME/plot чтобы увидеть пример графика."
