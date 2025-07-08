import subprocess
import sys
from typing import Callable


MENU_OPTIONS: dict[str, Callable[[], None]] = {}


def register(name: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def decorator(func: Callable[[], None]) -> Callable[[], None]:
        MENU_OPTIONS[name] = func
        return func
    return decorator


@register("1")
def build_image() -> None:
    """Собрать Docker образ из текущего каталога."""
    try:
        subprocess.run(["docker", "build", "-t", "myproject", "."], check=True)
        print("Образ myproject собран")
    except FileNotFoundError:
        print("Docker не установлен")
    except subprocess.CalledProcessError:
        print("Ошибка сборки образа")


@register("2")
def run_container() -> None:
    """Запустить контейнер из образа myproject."""
    name = input("Имя контейнера [myproject]: ").strip() or "myproject"
    try:
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "-p",
                "8000:8000",
                "--name",
                name,
                "myproject",
            ],
            check=True,
        )
        print(f"Контейнер {name} запущен на порту 8000")
    except FileNotFoundError:
        print("Docker не установлен")
    except subprocess.CalledProcessError:
        print("Не удалось запустить контейнер")


@register("3")
def fetch_api() -> None:
    url = input("Введите URL API: ").strip()
    if not url:
        print("URL не задан")
        return
    try:
        import requests
    except Exception:
        print("Модуль requests не установлен")
        return
    try:
        resp = requests.get(url)
        print(resp.text)
    except Exception as e:
        print(f"Ошибка запроса: {e}")


@register("q")
@register("0")
def quit_menu() -> None:
    sys.exit(0)


def main() -> None:
    while True:
        print("\nМеню:")
        print("1. Собрать Docker образ")
        print("2. Запустить контейнер")
        print("3. Получить ответ от API")
        print("0. Выход")
        choice = input("Выберите пункт: ").strip()
        action = MENU_OPTIONS.get(choice)
        if action:
            action()
        else:
            print("Неизвестный пункт")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
