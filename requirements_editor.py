from pathlib import Path
import argparse
import builtins

REQUIREMENTS_FILE = Path(__file__).with_name('proj_requirements.txt')


def load_requirements():
    if REQUIREMENTS_FILE.exists():
        return REQUIREMENTS_FILE.read_text(encoding='utf-8').splitlines()
    return []


def save_requirements(lines):
    REQUIREMENTS_FILE.write_text('\n'.join(lines), encoding='utf-8')


def edit_requirements():
    lines = load_requirements()
    print('Текущий список требований:\n')
    for line in lines:
        print(f'- {line}')
    print('\nВведите новые строки. Завершите ввод строкой EOF.')
    new_lines = []
    while True:
        line = builtins.input()
        if line == 'EOF':
            break
        new_lines.append(line)
    save_requirements(new_lines)
    print('Список требований обновлён.')


def main():
    parser = argparse.ArgumentParser(description='Управление требованиями')
    parser.add_argument('--edit', action='store_true', help='Редактировать список')
    args = parser.parse_args()
    if args.edit:
        edit_requirements()
    else:
        for req in load_requirements():
            print('-', req)


if __name__ == '__main__':
    main()
