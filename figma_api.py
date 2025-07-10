"""Клиент для REST API Figma."""

from __future__ import annotations

import os
import argparse
import json
from typing import Any, Dict

import requests

API_URL = "https://api.figma.com/v1"


class FigmaClient:
    """Минимальный интерфейс для запросов к API Figma."""

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("FIGMA_TOKEN", "")

    def _headers(self) -> Dict[str, str]:
        if not self.token:
            raise ValueError("Не указан токен API")
        return {"X-Figma-Token": self.token}

    def get_me(self) -> Dict[str, Any]:
        """Вернуть информацию о текущем пользователе."""
        resp = requests.get(f"{API_URL}/me", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def get_file(self, key: str) -> Dict[str, Any]:
        """Получить содержимое файла по ключу."""
        resp = requests.get(f"{API_URL}/files/{key}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def list_projects(self, team_id: str) -> Dict[str, Any]:
        """Список проектов указанной команды."""
        resp = requests.get(
            f"{API_URL}/teams/{team_id}/projects", headers=self._headers()
        )
        resp.raise_for_status()
        return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Запросы к Figma API")
    parser.add_argument("token", nargs="?", help="Токен доступа")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("me")
    f = sub.add_parser("file")
    f.add_argument("key")
    p = sub.add_parser("projects")
    p.add_argument("team_id")

    args = parser.parse_args()
    client = FigmaClient(args.token)
    if args.cmd == "me":
        data = client.get_me()
    elif args.cmd == "file":
        data = client.get_file(args.key)
    elif args.cmd == "projects":
        data = client.list_projects(args.team_id)
    else:
        parser.print_help()
        return
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

