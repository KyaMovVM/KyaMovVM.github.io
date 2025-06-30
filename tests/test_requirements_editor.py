import builtins
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from requirements_editor import load_requirements, save_requirements, edit_requirements


def test_edit_cycle(tmp_path, monkeypatch):
    monkeypatch.setattr("requirements_editor.REQUIREMENTS_FILE", tmp_path / "req.txt")
    save_requirements(["old"])
    inputs = iter(["new line", "EOF"])
    monkeypatch.setattr(builtins, "input", lambda: next(inputs))
    edit_requirements()
    assert load_requirements() == ["new line"]
