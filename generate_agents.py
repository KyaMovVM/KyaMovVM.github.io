import pathlib

ROOT = pathlib.Path(__file__).parent
DOCS = [ROOT / 'docs' / 'templates.md', ROOT / 'docs' / 'metaphors.md']
IMAGES = ['uml-diagram.svg', 'fail2ban-uml.svg']

GUIDELINES = [
    'Всегда выполняйте `pytest -q` и добавляйте вывод в раздел Testing описания PR.',
    'Если `nano` недоступен, используйте `sed` или `cat >` для редактирования файлов.',
    'Документацию пишите на русском языке, если не указано иное.',
    'Создавайте развёрнутые сообщения коммитов.'
]


def main() -> None:
    lines = ['# AGENT INSTRUCTIONS', '', 'Этот файл создан скриптом `generate_agents.py`.']
    lines.append('')
    lines.append('## Repo Guidelines')
    for g in GUIDELINES:
        lines.append(f'- {g}')
    lines.append('')
    lines.append('## UML')
    for img in IMAGES:
        lines.append(f'![{img}]({img})')
    lines.append('')
    lines.append('## Документация')
    for doc in DOCS:
        lines.append(f'### {doc.name}')
        lines.append('')
        lines.append(doc.read_text(encoding='utf-8'))
        lines.append('')
    (ROOT / 'AGENTS.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
