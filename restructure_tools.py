#!/usr/bin/env python3
"""Utilities for restructuring project files.

The script can format all Python modules using `isort` and `black`,
ensuring a consistent import order and code style. It also verifies that
each HTML page contains placeholders for the common header and footer so
that the layout remains uniform across the site."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent


def format_python() -> None:
    """Format all Python files using isort and black."""
    py_files = [str(p) for p in ROOT.rglob("*.py")]
    if not py_files:
        return
    print("Running isort and black on Python sources...")
    subprocess.check_call([sys.executable, "-m", "isort", *py_files])
    subprocess.check_call([sys.executable, "-m", "black", *py_files])


def update_html_layout() -> None:
    """Ensure every HTML page includes header/footer placeholders."""
    header = "<div id=\"header-placeholder\"></div>"
    footer = "<div id=\"footer-placeholder\"></div>"
    script_tag = "<script src=\"load_layout.js\" data-base=\"./\"></script>"

    html_files = [p for p in ROOT.glob("*.html") if p.name not in {"header.html", "footer.html"}]
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        changed = False
        if "header-placeholder" not in text:
            text = text.replace("<body", f"<body\n    {header}", 1)
            changed = True
        if "footer-placeholder" not in text:
            text = text.replace("</body>", f"    {footer}\n    {script_tag}\n</body>", 1)
            changed = True
        if changed:
            path.write_text(text, encoding="utf-8")
            print(f"Updated {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Restructure project files")
    parser.add_argument("--html", action="store_true", help="Update HTML layout")
    parser.add_argument("--python", action="store_true", help="Format Python code")
    args = parser.parse_args()

    if args.python:
        format_python()
    if args.html:
        update_html_layout()
    if not (args.python or args.html):
        parser.print_help()


if __name__ == "__main__":
    main()
    # Example usage:
    # python3 restructure_tools.py --python --html
