# KyaMovVM.github.io

Репозиторий содержит демонстрационный сайт с вращающейся 3D‑моделью автомобиля и базовыми страницами документации.
Все необходимые файлы Material Design Lite хранятся локально, поэтому подключение к `code.getmdl.io` не требуется.
Скрипт `backend_tools.py` показывает пример взаимодействия с сервером по SSH и отправки HTTP‑запросов.
Помимо статического размещения, сайт можно интегрировать в Django: скопируйте HTML и ресурсы в каталог `static` проекта и подключите страницы как шаблоны.

## Django Integration

Для удобства добавлен модуль `django_site`, предоставляющий готовые представления и маршруты на основе `TemplateView`. Скопируйте HTML-файлы в каталог `templates` и подключите `django_site.urls` в вашем `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path('', include('django_site.urls')),
]
```

## Страницы
- **index.html** – главная демонстрация с вращающимся автомобилем.
- **api.html** – упрощённый интерфейс просмотра логов сервера.
- **fail2ban.html** – вывод логов Fail2Ban.
- **docs.html** – краткая документация по API.
- **modules.html** – обзор структуры модулей проекта.
- **plan.html** – пошаговый план разработки.
- **crossref.html** – таблица перекрёстных ссылок на функции и методы.
- **json_intro.html** – краткое введение в JSON Schema.
- **docker_game.html** – интерактивная игра по запуску Docker Compose.

Каждая страница содержит пункт меню для отображения UML‑диаграммы (`uml-diagram.svg`). На странице Fail2Ban используется изображение <code>fail2ban-uml.svg</code>.
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
Скрипт `backend_tools.py` подключается к удалённому хосту по SSH и выполняет HTTP‑запросы.
Примерные учётные данные необходимо заменить перед использованием. Для GPU‑задач можно задействовать библиотеку [cuda-python](https://github.com/NVIDIA/cuda-python).

## Инструменты анализа

Скрипт `crossref.py` собирает перекрёстные ссылки на функции, методы и
переменные во всём проекте. Запуск с параметром `-o` создаст файл
`crossref.txt` с координатами объектов:

```bash
python crossref.py -o crossref.txt
```
Получившийся список можно просмотреть на странице `crossref.html`.

Для редактирования шаблонов ручного тестирования предназначен
`template_editor.py`. Без параметров он покажет список доступных шаблонов,
а передав имя файла – позволит заменить его содержимое.

## Инструменты реструктуризации

Скрипт `restructure_tools.py` автоматизирует приведение кода и HTML-шаблонов к единому виду и проверяет наличие общих блоков шапки и подвала на каждой странице.
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

Затем выполните тесты командой:

```bash
pytest -q
```
## Robots.txt и карта сайта
Поисковые системы должны обращаться к домену https://kyamovvm.com. Файл `robots.txt` указывает на `sitemap.xml`, где перечислены все HTML‑страницы проекта. В нём также прописана директива `Host: kyamovvm.com`, предотвращающая индексирование github.io.

## Manual Tests

Полный список ручных проверок приведён в файле [docs/manual_tests.html](docs/manual_tests.html). Пройдите по чек‑листу, чтобы убедиться, что каждая страница корректно отображает UML‑диаграммы и взаимодействует с сервером.
## Development Plan
Detailed steps for designing and maintaining the project are described in [development_plan.md](development_plan.md).
