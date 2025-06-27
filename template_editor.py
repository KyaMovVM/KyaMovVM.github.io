import argparse
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "templates"


def list_templates():
    return [p.name for p in TEMPLATE_DIR.glob("*.txt")]


def load_template(name):
    path = TEMPLATE_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Template {name} not found")
    return path.read_text(encoding="utf-8")


def save_template(name, content):
    path = TEMPLATE_DIR / name
    path.write_text(content, encoding="utf-8")


def edit_template(name):
    content = load_template(name)
    print("Текущее содержимое:\n")
    print(content)
    print("\nВведите новый текст. Завершите ввод строкой EOF на отдельной строке.")
    lines = []
    while True:
        line = input()
        if line == "EOF":
            break
        lines.append(line)
    new_content = "\n".join(lines)
    save_template(name, new_content)
    print(f"Шаблон {name} сохранён.")


def main():
    parser = argparse.ArgumentParser(description="Редактор шаблонов")
    parser.add_argument("name", nargs="?", help="Имя шаблона")
    args = parser.parse_args()

    if not args.name:
        print("Доступные шаблоны:")
        for t in list_templates():
            print(" -", t)
        return
    edit_template(args.name)


if __name__ == "__main__":
    main()
