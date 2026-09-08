"""Unit tests for the human reviewer helper script."""

from __future__ import annotations

from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from scripts import check_pr_human_reviewers as reviewers


@pytest.mark.unit
def test_summarize_reviews_counts_unique_humans_and_approvals() -> None:
    def fake_run(cmd, check, capture_output, text):
        if cmd[:3] == ["gh", "api", "repos/acme/widget/pulls/42/reviews"]:
            if (
                "--jq" in cmd
                and cmd[-1]
                == '[.[] | select(.user.type == "User") | {reviewer: .user.login, state: .state}]'
            ):
                return CompletedProcess(
                    cmd,
                    0,
                    stdout='[{"reviewer":"alice","state":"COMMENTED"},'
                    '{"reviewer":"alice","state":"APPROVED"},'
                    '{"reviewer":"bob","state":"COMMENTED"}]\n',
                    stderr="",
                )
        if cmd[:3] == ["gh", "pr", "view"]:
            return CompletedProcess(cmd, 0, stdout="bob\n", stderr="")
        raise AssertionError(f"Unexpected command: {cmd!r}")

    with patch.object(reviewers.subprocess, "run", side_effect=fake_run):
        summary = reviewers.summarize_reviews("acme", "widget", 42)

    assert summary.count == 2
    assert summary.approvals == 1
    assert [row.reviewer for row in summary.rows] == ["alice", "alice", "bob"]


@pytest.mark.unit
def test_main_auto_approves_when_no_human_reviewers_are_present() -> None:
    commands: list[list[str]] = []

    def fake_run(cmd, check, capture_output, text):
        commands.append(cmd)
        if cmd[:3] == ["gh", "api", "repos/acme/widget/pulls/42/reviews"]:
            if (
                "--jq" in cmd
                and cmd[-1]
                == '[.[] | select(.user.type == "User") | {reviewer: .user.login, state: .state}]'
            ):
                return CompletedProcess(cmd, 0, stdout="[]\n", stderr="")
        if cmd[:3] == ["gh", "api", "user"]:
            return CompletedProcess(cmd, 0, stdout="alice\n", stderr="")
        if cmd[:3] == ["gh", "pr", "view"]:
            return CompletedProcess(cmd, 0, stdout="bob\n", stderr="")
        if cmd[:3] == ["gh", "pr", "review"]:
            return CompletedProcess(cmd, 0, stdout="", stderr="")
        raise AssertionError(f"Unexpected command: {cmd!r}")

    with patch.object(reviewers.subprocess, "run", side_effect=fake_run):
        exit_code = reviewers.main(["acme", "widget", "42", "--approve-if-solo-human"])

    assert exit_code == 0
    assert any(cmd[:3] == ["gh", "pr", "review"] for cmd in commands)


@pytest.mark.unit
def test_main_refuses_auto_approval_when_multiple_humans_are_present() -> None:
    commands: list[list[str]] = []

    def fake_run(cmd, check, capture_output, text):
        commands.append(cmd)
        if cmd[:3] == ["gh", "api", "repos/acme/widget/pulls/42/reviews"]:
            if (
                "--jq" in cmd
                and cmd[-1]
                == '[.[] | select(.user.type == "User") | {reviewer: .user.login, state: .state}]'
            ):
                return CompletedProcess(
                    cmd,
                    0,
                    stdout='[{"reviewer":"alice","state":"COMMENTED"},'
                    '{"reviewer":"bob","state":"APPROVED"}]\n',
                    stderr="",
                )
        if cmd[:3] == ["gh", "api", "user"]:
            return CompletedProcess(cmd, 0, stdout="alice\n", stderr="")
        if cmd[:3] == ["gh", "pr", "view"]:
            return CompletedProcess(cmd, 0, stdout="bob\n", stderr="")
        raise AssertionError(f"Unexpected command: {cmd!r}")

    with patch.object(reviewers.subprocess, "run", side_effect=fake_run):
        exit_code = reviewers.main(["acme", "widget", "42", "--approve-if-solo-human"])

    assert exit_code == 2
    assert not any(cmd[:3] == ["gh", "pr", "review"] for cmd in commands)


@pytest.mark.unit
def test_main_skips_auto_approval_for_self_authored_pr() -> None:
    commands: list[list[str]] = []

    def fake_run(cmd, check, capture_output, text):
        commands.append(cmd)
        if cmd[:3] == ["gh", "api", "repos/acme/widget/pulls/42/reviews"]:
            if (
                "--jq" in cmd
                and cmd[-1]
                == '[.[] | select(.user.type == "User") | {reviewer: .user.login, state: .state}]'
            ):
                return CompletedProcess(cmd, 0, stdout="[]\n", stderr="")
        if cmd[:3] == ["gh", "api", "user"]:
            return CompletedProcess(cmd, 0, stdout="alice\n", stderr="")
        if cmd[:3] == ["gh", "pr", "view"]:
            return CompletedProcess(cmd, 0, stdout="alice\n", stderr="")
        raise AssertionError(f"Unexpected command: {cmd!r}")

    with patch.object(reviewers.subprocess, "run", side_effect=fake_run):
        exit_code = reviewers.main(["acme", "widget", "42", "--approve-if-solo-human"])

    assert exit_code == 2
    assert not any(cmd[:3] == ["gh", "pr", "review"] for cmd in commands)


@pytest.mark.unit
def test_parse_args_rejects_non_positive_pr_number() -> None:
    with pytest.raises(SystemExit):
        reviewers.parse_args(["acme", "widget", "0"])


@pytest.mark.unit
def test_main_returns_2_for_malformed_review_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_run(cmd, check, capture_output, text):
        if cmd[:3] == ["gh", "api", "repos/acme/widget/pulls/42/reviews"]:
            return CompletedProcess(cmd, 0, stdout="{bad-json", stderr="")
        raise AssertionError(f"Unexpected command: {cmd!r}")

    with patch.object(reviewers.subprocess, "run", side_effect=fake_run):
        exit_code = reviewers.main(["acme", "widget", "42", "--count"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "error:" in captured.err
