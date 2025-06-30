import argparse
import shutil
from pathlib import Path

EXCLUDE = {".git", "docs", "tests", "__pycache__"}
EXT_SKIP = {".py", ".md"}


def should_copy(path: Path) -> bool:
    if path.name in EXCLUDE:
        return False
    if path.suffix in EXT_SKIP:
        return False
    return True


def deploy(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if not should_copy(item):
            continue
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def deploy_django(src: Path, project: Path) -> None:
    templates = project / 'templates'
    static = project / 'static'
    templates.mkdir(parents=True, exist_ok=True)
    static.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if not should_copy(item):
            continue
        if item.suffix == '.html':
            target = templates / item.name
            shutil.copy2(item, target)
        else:
            target = static / item.name
            if item.is_dir():
                shutil.copytree(item, target, dirs_exist_ok=True)
            else:
                shutil.copy2(item, target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Копирование файлов сайта в целевую директорию'
    )
    parser.add_argument('target', nargs='?', help='Путь назначения')
    parser.add_argument('--django', help='Путь к корню Django-проекта')
    args = parser.parse_args()

    src = Path(__file__).parent
    if args.django:
        deploy_django(src, Path(args.django))
        print(f'Файлы скопированы в {args.django}/templates и {args.django}/static')
    elif args.target:
        deploy(src, Path(args.target))
        print(f'Файлы скопированы в {args.target}')
    else:
        parser.error('Не указан путь назначения или параметр --django')
