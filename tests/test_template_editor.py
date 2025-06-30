import os
import builtins
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from template_editor import list_templates, load_template, save_template


def test_list_templates():
    templates = list_templates()
    assert "base_template.txt" in templates


def test_edit_cycle(tmp_path, monkeypatch):
    monkeypatch.setattr("template_editor.TEMPLATE_DIR", tmp_path)
    save_template("temp.txt", "old")

    inputs = iter(["new line", "EOF"])
    monkeypatch.setattr(builtins, "input", lambda: next(inputs))
    from template_editor import edit_template

    edit_template("temp.txt")
    assert load_template("temp.txt") == "new line"
    os.remove(tmp_path / "temp.txt")
