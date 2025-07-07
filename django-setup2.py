#!/usr/bin/env python3
"""Упрощённый установщик Django-проекта.

Скрипт создаёт проект, приложение и настраивает базовые параметры
`settings.py`. Он не требует root-прав и подходит для начального
развёртывания в домашнем каталоге пользователя.
"""

import argparse
import os
import re
import subprocess
from pathlib import Path


def run(cmd: str, cwd: Path | None = None) -> None:
    """Выполнить команду и вывести её на экран."""
    print(f"> {cmd}")
    subprocess.check_call(cmd, shell=True, cwd=cwd)


def ensure_venv(project_dir: Path) -> tuple[Path, Path]:
    """Создать виртуальное окружение при отсутствии."""
    venv = project_dir / "venv"
    if not venv.exists():
        run("python3 -m venv venv", cwd=project_dir)
    pip = venv / "bin" / "pip"
    python = venv / "bin" / "python"
    return pip, python


def install_packages(pip: Path) -> None:
    """Установить набор пакетов для продакшн-окружения."""
    pkgs = [
        "django",
        "psycopg[binary]",
        "gunicorn",
        "whitenoise",
        "django-environ",
        "django-extensions",
        "djangorestframework",
        "drf-yasg",
        "celery",
        "channels",
        "django-cors-headers",
        "matplotlib",
        "pillow",
    ]
    run(f"{pip} install --upgrade " + " ".join(pkgs))


def start_project(project_dir: Path, project: str) -> None:
    if not (project_dir / "manage.py").exists():
        run(f"django-admin startproject {project} .", cwd=project_dir)


def start_app(project_dir: Path, python: Path, app: str) -> None:
    if not (project_dir / app).exists():
        run(f"{python} manage.py startapp {app}", cwd=project_dir)


def update_settings(settings: Path, app: str, host: str) -> None:
    text = settings.read_text(encoding="utf-8")
    if "environ" not in text:
        text = text.replace(
            "from pathlib import Path",
            "from pathlib import Path\nimport environ",
            1,
        )
        text = text.replace(
            "BASE_DIR = Path(__file__).resolve().parent.parent",
            "BASE_DIR = Path(__file__).resolve().parent.parent\n\n"
            "env = environ.Env()\n"
            "environ.Env.read_env(BASE_DIR / '.env')",
            1,
        )

    if "INSTALLED_APPS = [" in text and app not in text:
        text = text.replace(
            "INSTALLED_APPS = [",
            "INSTALLED_APPS = [\n    'rest_framework',\n    'corsheaders',\n"
            "    'django_extensions',\n    'drf_yasg',\n    'channels',\n"
            f"    '{app}',",
            1,
        )

    text = re.sub(r"ALLOWED_HOSTS = .*", f"ALLOWED_HOSTS = ['{host}']", text)
    text = re.sub(r"DEBUG = .*", "DEBUG = env.bool('DJANGO_DEBUG', False)", text)
    if "SECRET_KEY" in text:
        text = re.sub(r"SECRET_KEY = .*", "SECRET_KEY = env('DJANGO_SECRET_KEY')", text)
    if "MIDDLEWARE = [" in text and "WhiteNoiseMiddleware" not in text:
        text = text.replace(
            "MIDDLEWARE = [",
            "MIDDLEWARE = [\n    'corsheaders.middleware.CorsMiddleware',\n"
            "    'whitenoise.middleware.WhiteNoiseMiddleware',",
            1,
        )
    if "STATIC_ROOT" not in text:
        text += (
            "\nSTATIC_ROOT = BASE_DIR / 'static'\n"
            "MEDIA_ROOT = BASE_DIR / 'media'\n"
            "CSRF_TRUSTED_ORIGINS = ['https://" + host + "']\n"
            "CHANNEL_LAYERS = {\n"
            "    'default': {\n"
            "        'BACKEND': 'channels.layers.InMemoryChannelLayer',\n"
            "    }\n"
            "}\n"
        )
    settings.write_text(text, encoding="utf-8")


def add_demo_view(app_dir: Path) -> None:
    view = app_dir / "views.py"
    if "plot_view" in view.read_text(encoding="utf-8", errors="ignore"):
        return
    view.write_text(
        "from django.http import HttpResponse\n"
        "import matplotlib.pyplot as plt\n"
        "import io, base64, urllib\n\n"
        "def plot_view(request):\n"
        "    fig, ax = plt.subplots()\n"
        "    ax.plot([1,2,3,4], [10,20,25,30])\n"
        "    buf = io.BytesIO()\n"
        "    plt.savefig(buf, format='png')\n"
        "    buf.seek(0)\n"
        "    img = base64.b64encode(buf.read())\n"
        "    uri = 'data:image/png;base64,' + urllib.parse.quote(img)\n"
        "    return HttpResponse(f'<img src={uri}/>')\n",
        encoding="utf-8",
    )

    urls = app_dir / "urls.py"
    if not urls.exists():
        urls.write_text(
            "from django.urls import path\n"
            "from . import views\n\n"
            "urlpatterns = [\n    path('plot/', views.plot_view, name='plot'),\n]\n",
            encoding="utf-8",
        )


def add_include(project_urls: Path, app: str) -> None:
    text = project_urls.read_text(encoding="utf-8")
    if f"include('{app}.urls')" in text:
        return
    text = text.replace(
        "from django.urls import path",
        "from django.urls import path, include",
        1,
    )
    text = text.replace(
        "urlpatterns = [",
        f"urlpatterns = [\n    path('', include('{app}.urls')),",
        1,
    )
    project_urls.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initial Django setup")
    parser.add_argument("project", help="Имя проекта")
    parser.add_argument("app", help="Имя приложения")
    parser.add_argument("host", help="Домен или IP")
    parser.add_argument("--base", default=str(Path.home() / "django-projects"), help="Каталог проектов")
    args = parser.parse_args()

    project_dir = Path(args.base) / args.project
    project_dir.mkdir(parents=True, exist_ok=True)

    env_file = project_dir / ".env"
    if not env_file.exists():
        sample = Path(__file__).with_name(".env.example")
        if sample.exists():
            env_file.write_text(sample.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            env_file.write_text("DJANGO_SECRET_KEY=changeme\n", encoding="utf-8")

    pip, python = ensure_venv(project_dir)
    install_packages(pip)

    start_project(project_dir, args.project)
    start_app(project_dir, python, args.app)

    settings = project_dir / args.project / "settings.py"
    update_settings(settings, args.app, args.host)

    run(f"{python} manage.py migrate", cwd=project_dir)
    run(f"{python} manage.py collectstatic --noinput", cwd=project_dir)

    add_demo_view(project_dir / args.app)
    add_include(project_dir / args.project / "urls.py", args.app)

    print("Setup complete. Запустите сервер командой:")
    print(f"{python} manage.py runserver 0.0.0.0:8000")


if __name__ == "__main__":
    main()
