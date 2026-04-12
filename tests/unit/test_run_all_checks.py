"""Unit tests for run_all_checks utility script."""

from types import SimpleNamespace

import pytest

from britecore_sdk.utils import run_all_checks


@pytest.mark.unit
def test_run_script_calls_subprocess_with_explicit_args(monkeypatch):
    """run_script invokes subprocess with the Python executable and script path."""
    calls = []

    def fake_run(cmd, check):
        calls.append((cmd, check))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(run_all_checks.subprocess, "run", fake_run)

    run_all_checks.run_script("check_site_configs.py")

    assert calls == [
        (
            [
                run_all_checks.sys.executable,
                run_all_checks.UTILS_DIR + "check_site_configs.py",
            ],
            False,
        )
    ]


@pytest.mark.unit
def test_run_script_exits_with_return_code_on_failure(monkeypatch):
    """run_script exits using child return code when a script fails."""
    monkeypatch.setattr(
        run_all_checks.subprocess,
        "run",
        lambda _cmd, check: SimpleNamespace(returncode=3),
    )

    with pytest.raises(SystemExit) as exc:
        run_all_checks.run_script("check_test_data.py")

    assert exc.value.code == 3


@pytest.mark.unit
def test_main_runs_all_scripts_in_order(monkeypatch):
    """main executes each configured script in order."""
    seen = []
    monkeypatch.setattr(run_all_checks, "SCRIPTS", ["a.py", "b.py"])
    monkeypatch.setattr(
        run_all_checks, "run_script", lambda script: seen.append(script)
    )

    run_all_checks.main()

    assert seen == ["a.py", "b.py"]
