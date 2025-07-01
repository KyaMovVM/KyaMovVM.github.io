#!/bin/bash

set -e

# Скрипт разворачивает Django-проект под Apache и mod_wsgi.
# Он старается не перезаписывать существующие файлы,
# поэтому подходит для донастройки уже созданного проекта.

echo "=== Django + Apache + mod_wsgi setup ==="

read -p "Введите имя проекта (например: mysite): " PROJECT_NAME
read -p "Введите имя приложения (например: app): " APP_NAME
read -p "Введите домен или IP для ALLOWED_HOSTS: " HOSTNAME

PROJECT_DIR="/srv/django/${PROJECT_NAME}"

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

APACHE_CONF="/etc/apache2/sites-available/${PROJECT_NAME}.conf"
echo "Создаю Apache конфиг..."
sudo bash -c "cat > $APACHE_CONF" <<EOV
<VirtualHost *:80>
    ServerName $HOSTNAME

    Alias /static/ $PROJECT_DIR/static/
    <Directory $PROJECT_DIR/static>
        Require all granted
    </Directory>

    Alias /media/ $PROJECT_DIR/media/
    <Directory $PROJECT_DIR/media>
        Require all granted
    </Directory>

    WSGIDaemonProcess $PROJECT_NAME python-home=$PROJECT_DIR/venv python-path=$PROJECT_DIR
    WSGIProcessGroup $PROJECT_NAME
    WSGIScriptAlias / $PROJECT_DIR/${PROJECT_NAME}/wsgi.py

    <Directory $PROJECT_DIR/${PROJECT_NAME}>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    ErrorLog \${APACHE_LOG_DIR}/${PROJECT_NAME}_error.log
    CustomLog \${APACHE_LOG_DIR}/${PROJECT_NAME}_access.log combined
</VirtualHost>
EOV

sudo a2ensite ${PROJECT_NAME}
sudo systemctl reload apache2

echo "Права на проект для www-data..."
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chmod -R 755 $PROJECT_DIR

echo "=== Готово! ==="
echo "Перейди в браузер на http://$HOSTNAME/plot чтобы увидеть пример графика."
