import importlib.util
import sys
from pathlib import Path

import pytest

UTIL_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "britecore_sdk"
    / "utils"
    / "check_markdown_structure.py"
)

spec = importlib.util.spec_from_file_location(
    "check_markdown_structure", str(UTIL_PATH)
)
assert spec is not None
assert spec.loader is not None
check_markdown_structure = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = check_markdown_structure
spec.loader.exec_module(check_markdown_structure)


@pytest.mark.unit
def test_analyze_markdown_text_flags_standalone_checkmark_line():
    issues = check_markdown_structure.analyze_markdown_text(
        "## Features\n\n✅ **Feature** — Description\n", Path("README.md")
    )

    assert len(issues) == 1
    assert issues[0].line_number == 3
    assert "Markdown list marker" in issues[0].message


@pytest.mark.unit
def test_analyze_markdown_text_allows_real_list_item():
    issues = check_markdown_structure.analyze_markdown_text(
        "## Features\n\n- ✅ **Feature** — Description\n", Path("README.md")
    )

    assert issues == []


@pytest.mark.unit
def test_analyze_markdown_text_ignores_checkmark_inside_fenced_code_block():
    issues = check_markdown_structure.analyze_markdown_text(
        "```text\n✅ This is example output\n```\n", Path("README.md")
    )

    assert issues == []


@pytest.mark.unit
def test_analyze_markdown_text_flags_unclosed_fence():
    issues = check_markdown_structure.analyze_markdown_text(
        "## Example\n\n```python\nprint('oops')\n", Path("README.md")
    )

    assert len(issues) == 1
    assert issues[0].message == "Unclosed fenced code block."


@pytest.mark.unit
def test_iter_markdown_files_excludes_generated_directories(tmp_path):
    authored = tmp_path / "README.md"
    authored.write_text("# ok\n", encoding="utf-8")
    generated = tmp_path / "build" / "artifact.md"
    generated.parent.mkdir()
    generated.write_text("# generated\n", encoding="utf-8")

    files = check_markdown_structure.iter_markdown_files(tmp_path)

    assert files == [authored]


@pytest.mark.unit
def test_main_returns_success_for_clean_markdown(tmp_path, monkeypatch, capsys):
    markdown_file = tmp_path / "README.md"
    markdown_file.write_text("# Title\n\n- ✅ Good item\n", encoding="utf-8")
    monkeypatch.setattr(check_markdown_structure, "REPO_ROOT", tmp_path)

    exit_code = check_markdown_structure.main([])

    assert exit_code == 0
    assert "passed" in capsys.readouterr().out


@pytest.mark.unit
def test_main_returns_failure_for_bad_markdown(tmp_path, monkeypatch, capsys):
    markdown_file = tmp_path / "README.md"
    markdown_file.write_text("# Title\n\n✅ Bad item\n", encoding="utf-8")
    monkeypatch.setattr(check_markdown_structure, "REPO_ROOT", tmp_path)

    exit_code = check_markdown_structure.main([])

    assert exit_code == 1
    output = capsys.readouterr().out
    assert "README.md:3" in output
    assert "Found 1 Markdown structure issue(s)." in output

