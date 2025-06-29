import argparse
import shutil
from pathlib import Path

EXCLUDE = {'.git', 'docs', 'tests', '__pycache__'}
EXT_SKIP = {'.py', '.md'}


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Копирование статических файлов в указанную директорию'
    )
    parser.add_argument('target', help='Путь назначения')
    args = parser.parse_args()
    deploy(Path(__file__).parent, Path(args.target))
    print(f'Файлы скопированы в {args.target}')
