# KyaMovVM.github.io

This repository hosts a simple demo site with a rotating 3D car and Material Design colors.
Additional pages provide an API log viewer and basic documentation. A small Python
В проект включены локальные файлы Material Design Lite, поэтому подключение к code.getmdl.io не требуется.
script (`backend_tools.py`) demonstrates how backend interactions over SSH and
HTTP requests could be performed.

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

## Manual Tests

Полный список ручных проверок приведён в файле [docs/manual_tests.md](docs/manual_tests.md). Пройдите по чек‑листу, чтобы убедиться, что каждая страница корректно отображает UML‑диаграммы и взаимодействует с сервером.
## Development Plan
Detailed steps for designing and maintaining the project are described in [development_plan.md](development_plan.md).
