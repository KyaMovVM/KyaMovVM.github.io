# KyaMovVM.github.io

This repository hosts a simple demo site with a rotating 3D car and Material Design colors.
Additional pages provide an API log viewer and basic documentation. A small Python
В проект включены локальные файлы Material Design Lite, поэтому подключение к code.getmdl.io не требуется.
script (`backend_tools.py`) demonstrates how backend interactions over SSH and
HTTP requests could be performed.
Кроме статического варианта сайт может быть размещён как приложение Django. Скопируйте HTML и ресурсы в каталог `static` проекта и подключите страницы как шаблоны.

## Django Integration

Для удобства добавлен модуль `django_site`, предоставляющий готовые представления и маршруты на основе `TemplateView`. Скопируйте HTML-файлы в каталог `templates` и подключите `django_site.urls` в вашем `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path('', include('django_site.urls')),
]
```

## Pages
- **index.html** – main demo with the 3D car animation.
- **api.html** – placeholder interface for viewing backend logs.
- **fail2ban.html** – interface for viewing Fail2Ban logs.
- **docs.html** – minimal API documentation.
- **modules.html** – обзор структуры модулей проекта.
- **plan.html** – пошаговый план разработки.
- **crossref.html** – таблица перекрёстных ссылок на функции и методы.
- **json_intro.html** – краткое введение в JSON Schema.

Each page includes a menu entry to show a transparent UML overlay with a simple architecture diagram (`uml-diagram.svg`). The Fail2Ban page uses <code>fail2ban-uml.svg</code>.
Окно диаграммы располагается поверх остальных элементов страницы и имеет полупрозрачный фон.
Для загрузки меню и подвала теперь используется скрипт `load_layout.js`. Укажите атрибут `data-base` с относительным путём к ресурсам, чтобы страница работала в любой папке, например `/usr/share/django-projects/welcome/static`:
```html
<div id="footer-placeholder"></div>
<script src="load_layout.js" data-base="./"></script>
```
Для копирования сайта в целевой каталог запустите
`python3 deploy_static.py /usr/share/django-projects/welcome/static`.
Если нужен полный перенос в Django‑проект одной командой, используйте
`python3 deploy_static.py --django /path/to/project`. Файлы автоматически
окажутся в подкаталогах `templates` и `static` указанного проекта.


## Backend script
`backend_tools.py` connects to a host via SSH and performs HTTP GET requests.
It is only an example, credentials must be updated before use. GPU tasks can
be prototyped using the [cuda-python](https://github.com/NVIDIA/cuda-python)
library.

## Инструменты анализа

Скрипт `crossref.py` собирает перекрёстные ссылки на функции, методы и
переменные во всём проекте. Запуск с параметром `-o` создаст файл
`crossref.txt` с координатами объектов:

```bash
python crossref.py -o crossref.txt
```

Для редактирования шаблонов ручного тестирования предназначен
`template_editor.py`. Без параметров он покажет список доступных шаблонов,
а передав имя файла – позволит заменить его содержимое.

## Инструменты реструктуризации

Скрипт `restructure_tools.py` автоматизирует приведение кода и HTML-шаблонов к единому виду.
Для форматирования Python выполните:

```bash
python3 restructure_tools.py --python
```

Для обновления HTML-файлов:

```bash
python3 restructure_tools.py --html
```

## Django Setup

Скрипт `djangosetup.py` автоматизирует разворачивание проекта под Apache.
Он совместим с Python 3.6, поэтому может выполняться даже на устаревших
серверах без обновления интерпретатора.
Перед запуском установите зависимости:

```bash
pip install django gunicorn matplotlib pillow
```

После этого выполните скрипт и следуйте инструкциям в терминале.

Новая версия `django-setup2.py` выполняет те же шаги, но не требует
root-прав и подходит для локального развертывания.

### Продакшн стек

Для развёртывания с поддержкой PostgreSQL, Celery и WebSocket установите
пакеты из `prod_requirements.txt`:

```bash
pip install -r prod_requirements.txt
```

Скрипт создаст файл `.env` по образцу `.env.example` и добавит базовые
настройки `django-environ`, WhiteNoise и подключение к PostgreSQL.



## Генерация AGENTS.md

После изменения файлов в каталоге `docs` или UML-диаграмм
запустите скрипт `generate_agents.py`. Он обновит файл `AGENTS.md`,
вставив в него текущее содержимое документации и изображения диаграмм.

## Tests
Unit tests находятся в директории `tests` и файле
`test_backend_tools.py`. Чтобы их запустить, сначала установите
зависимости:

```bash
pip install -r requirements.txt
```

Then execute the tests with:

```bash
pytest -q
```
## Robots.txt и карта сайта
Поисковые системы должны обращаться к домену https://kyamovvm.com. Файл `robots.txt` указывает на `sitemap.xml`, где перечислены все HTML‑страницы проекта. В нём также прописана директива `Host: kyamovvm.com`, предотвращающая индексирование github.io.

## Manual Tests

Полный список ручных проверок приведён в файле [docs/manual_tests.html](docs/manual_tests.html). Пройдите по чек‑листу, чтобы убедиться, что каждая страница корректно отображает UML‑диаграммы и взаимодействует с сервером.
## Development Plan
Detailed steps for designing and maintaining the project are described in [development_plan.md](development_plan.md).
