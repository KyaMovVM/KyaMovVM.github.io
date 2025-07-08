from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def application(environ, start_response):
    """Простейшее WSGI-приложение для демонстрации."""
    path = environ.get("PATH_INFO", "/").lstrip("/")
    file_path = BASE_DIR / path
    if not file_path.exists() or file_path.is_dir():
        status = "404 Not Found"
        content = b"Not Found"
    else:
        status = "200 OK"
        content = file_path.read_bytes()
    start_response(status, [("Content-Type", "text/html; charset=utf-8"),
                            ("Content-Length", str(len(content)))])
    return [content]
