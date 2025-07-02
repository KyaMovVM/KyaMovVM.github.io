#!/usr/bin/env python3
"""Автоматическая настройка Django-проекта под Apache.

Этот скрипт повторяет шаги `setup_django.sh`, но реализован на Python.
Дополнительно имеется функция анализа ошибок и логов Apache через
OpenAI API с сервером LM Studio.
"""


import os
import re
import subprocess
from pathlib import Path
from typing import Optional

try:
    import openai
except Exception:
    openai = None  # библиотека может быть не установлена


API_BASE = os.getenv("LM_API_BASE", "http://localhost:1234/v1")
MODEL_NAME = os.getenv("LM_MODEL", "lmstudio")


def ask(prompt: str, default: str = "") -> str:
    """Запрос значения у пользователя с поддержкой значения по умолчанию."""
    value = input(prompt)
    return value.strip() or default


def analyze_log(text: str) -> str:
    """Вернуть подсказку по исправлению ошибки через LM Studio."""
    if openai is None:
        return "Модуль openai не установлен"
    client = openai.OpenAI(api_key="lm-studio", base_url=API_BASE)
    msg = [
        {
            "role": "system",
            "content": "Помоги диагностировать проблемы установки Django и Apache.",
        },
        {"role": "user", "content": f"Лог ошибки:\n{text}"},
    ]
    try:
        resp = client.chat.completions.create(model=MODEL_NAME, messages=msg)
        return resp.choices[0].message.content.strip()
    except Exception as e:  # noqa: BLE001
        return f"Ошибка запроса: {e}"


def run(cmd: str, cwd: Optional[Path] = None) -> None:
    """Выполнить команду, вывести вывод и при ошибке предложить анализ."""
    print(f">> {cmd}")
    proc = subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=cwd)
    if proc.returncode != 0:
        print(proc.stderr)
        print(analyze_log(proc.stderr))
        raise RuntimeError(f"Команда завершилась ошибкой: {cmd}")
    if proc.stdout:
        print(proc.stdout)


def ensure_deps() -> None:
    """Install system packages required for mod_wsgi and Pillow."""
    if subprocess.run("command -v apxs", shell=True).returncode != 0:
        print("Команда apxs отсутствует. Пытаюсь установить dev-пакет Apache...")
        if subprocess.run("command -v apt-get", shell=True).returncode == 0:
            run("sudo apt-get update")
            run("sudo apt-get install -y apache2-dev libapache2-mod-wsgi-py3")
        elif subprocess.run("command -v yum", shell=True).returncode == 0:
            run("sudo yum install -y httpd-devel mod_wsgi")
        else:
            print("Не удалось определить менеджер пакетов. Установите apxs вручную.")

    if subprocess.run("command -v apt-get", shell=True).returncode == 0:
        run("sudo apt-get install -y libjpeg-dev zlib1g-dev")
    elif subprocess.run("command -v yum", shell=True).returncode == 0:
        run("sudo yum install -y libjpeg-devel zlib-devel")


def modify_settings(settings: Path, app_name: str, host: str) -> None:
    text = settings.read_text(encoding="utf-8")
    if app_name not in text:
        text = re.sub(
            r"INSTALLED_APPS = \[",
            f"INSTALLED_APPS = [\n    '{app_name}',",
            text,
            count=1,
        )
    text = re.sub(r"ALLOWED_HOSTS = .+", f"ALLOWED_HOSTS = ['{host}']", text)
    text = re.sub(r"DEBUG = True", "DEBUG = False", text)
    if "STATIC_ROOT" not in text:
        text += "\nSTATIC_ROOT = BASE_DIR / 'static'\nMEDIA_ROOT = BASE_DIR / 'media'\n"
    settings.write_text(text, encoding="utf-8")


def main() -> None:
    print("=== Django + Apache + mod_wsgi setup ===")
    project = ask("Введите имя проекта (например: mysite): ")
    app = ask("Введите имя приложения (например: app): ")
    host = ask("Введите домен или IP для ALLOWED_HOSTS: ")
    base = ask(
        "Каталог для проектов [/usr/share/django-projects]: ",
        "/usr/share/django-projects",
    )
    project_dir = Path(base) / project

    print("== Проверка окружения ==")
    print(f"Проект: {project}")
    print(f"Приложение: {app}")
    print(f"Хост: {host}")
    print(f"Каталог проекта: {project_dir}")

    if not project_dir.exists():
        run(f"sudo mkdir -p {project_dir}")
        run(f"sudo chown $USER:$USER {project_dir}")

    if not (project_dir / "venv").exists():
        run("python3 -m venv venv", cwd=project_dir)

    pip = project_dir / "venv/bin/pip"
    python = project_dir / "venv/bin/python"

    ensure_deps()

    run(f"{pip} install --upgrade django gunicorn matplotlib pillow")

    if (
        not (project_dir / project / "settings.py").exists()
        and not (project_dir / "manage.py").exists()
    ):
        run(f"django-admin startproject {project} .", cwd=project_dir)

    if not (project_dir / app).exists():
        run(f"{python} manage.py startapp {app}", cwd=project_dir)

    settings = project_dir / project / "settings.py"
    modify_settings(settings, app, host)

    run(f"{python} manage.py migrate", cwd=project_dir)
    run(f"{python} manage.py collectstatic --noinput", cwd=project_dir)

    views_file = project_dir / app / "views.py"
    if "plot_view" not in views_file.read_text(encoding="utf-8", errors="ignore"):
        views_file.write_text(
            "from django.http import HttpResponse\n"
            "import matplotlib.pyplot as plt\n"
            "import io, urllib, base64\n\n"
            "def plot_view(request):\n"
            "    fig, ax = plt.subplots()\n"
            "    ax.plot([1,2,3,4],[10,20,25,30])\n"
            "    buf = io.BytesIO()\n"
            "    plt.savefig(buf, format='png')\n"
            "    buf.seek(0)\n"
            "    img = base64.b64encode(buf.read())\n"
            "    uri = 'data:image/png;base64,' + urllib.parse.quote(img)\n"
            "    return HttpResponse(f'<img src={uri}/>')\n",
            encoding="utf-8",
        )

    urls = project_dir / app / "urls.py"
    if not urls.exists():
        urls.write_text(
            "from django.urls import path\n"
            "from . import views\n\n"
            "urlpatterns = [\n    path('plot/', views.plot_view, name='plot'),\n]\n",
            encoding="utf-8",
        )

    proj_urls = project_dir / project / "urls.py"
    url_text = proj_urls.read_text(encoding="utf-8")
    if f"include('{app}.urls')" not in url_text:
        url_text = re.sub(
            r"from django.urls import path",
            "from django.urls import path, include",
            url_text,
            count=1,
        )
        url_text = re.sub(
            r"urlpatterns = \[",
            f"urlpatterns = [\n    path('', include('{app}.urls')),",
            url_text,
            count=1,
        )
        proj_urls.write_text(url_text, encoding="utf-8")

    apache_conf = Path("/etc/apache2/sites-available/000-default-le-ssl.conf")
    http_conf = Path("/etc/apache2/sites-available/000-default.conf")
    conf_content = f"""
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerAdmin kyamovvm@gmail.com
    ServerName {host}
    ServerAlias www.{host}
    DocumentRoot {base}/

    ErrorLog {{APACHE_LOG_DIR}}/error.log
    CustomLog {{APACHE_LOG_DIR}}/access.log combined

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/{host}/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/{host}/privkey.pem

    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Permissions-Policy "geolocation=(), microphone=()"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"

    WSGIDaemonProcess {project} python-home={project_dir}/venv python-path={project_dir} user=www-data group=www-data
    WSGIProcessGroup {project}
    WSGIScriptAlias / {project_dir}/{project}/wsgi.py

    <Directory {project_dir}/{project}>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    Alias /static/ {project_dir}/static/
    <Directory {project_dir}/static>
        Require all granted
    </Directory>
</VirtualHost>
</IfModule>
"""
    http_content = f"""
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    ServerName {host}
    ServerAlias www.{host}

    Redirect permanent / https://{host}/
</VirtualHost>
"""
    run(f"sudo bash -c 'cat > {apache_conf}'", cwd=None)
    with open("cmd.sh", "w", encoding="utf-8") as f:
        f.write(f"cat <<'EOF' > {apache_conf}\n{conf_content}\nEOF\n")
    run(f"sudo bash cmd.sh && rm cmd.sh")
    with open("cmd.sh", "w", encoding="utf-8") as f:
        f.write(f"cat <<'EOF' > {http_conf}\n{http_content}\nEOF\n")
    run(f"sudo bash cmd.sh && rm cmd.sh")
    run("sudo systemctl reload apache2")

    run(f"sudo chown -R www-data:www-data {project_dir}")
    run(f"sudo chmod -R 755 {project_dir}")

    log_file = Path(os.getenv("APACHE_LOG", "/var/log/apache2/error.log"))
    if not log_file.exists():
        log_file = Path("/var/log/httpd/error_log")
    if log_file.exists():
        text = subprocess.run(
            ["sudo", "tail", "-n", "20", str(log_file)],
            text=True,
            capture_output=True,
        ).stdout
        print("Последние сообщения Apache:")
        print(text)
        print(analyze_log(text))

    print("=== Готово! ===")
    print(f"Перейдите в браузер на http://{host}/plot чтобы увидеть пример графика.")


if __name__ == "__main__":
    main()
