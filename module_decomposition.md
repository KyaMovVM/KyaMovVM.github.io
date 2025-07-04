# Декомпозиция проекта по книге "Совершенный код"

Ниже приведена примерная структура модулей сайта, следуя советам из "Совершенного кода" о разделении ответственности и снижении связности:

1. **UI** – статические страницы (`index.html`, `api.html`, `docs.html`), отвечающие только за отображение и взаимодействие пользователя с интерфейсом.
   Отдельная страница `fail2ban.html` показывает логи Fail2Ban.
2. **Style** – общие таблицы стилей (`styles.css`), оформляющие внешний вид всех страниц.
3. **Scripts** – клиентские скрипты для анимаций и вспомогательных функций. При необходимости могут быть вынесены в отдельные JS‑модули.
4. **Backend** – логика работы с сервером, включающая `backend_tools.py` и возможные вспомогательные модули (например, `ssh_utils.py`, `http_utils.py`).
5. **GPU** – вычислительные функции с применением библиотеки [cuda-python](https://github.com/NVIDIA/cuda-python).
6. **Tests** – модульные тесты, такие как `test_backend_tools.py`, проверяющие отдельные функции без участия пользовательского интерфейса.
7. **Documentation** – файлы с описанием API и планом развития проекта (`docs.html`, `development_plan.md`).
8. **Manual** – шаблоны и инструкции для ручных проверок (`templates/`, `docs/manual_tests.html`).

Такое разделение позволит развивать каждую часть проекта независимо и делать код более поддерживаемым.
