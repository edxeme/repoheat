"""CLI tests: text tables, JSON output and error handling."""

import json

import pytest

from repoheat.cli import main


def test_churn_text_output(make_repo, capsys):
    assert main(["churn", str(make_repo())]) == 0

    out = capsys.readouterr().out
    assert "src/core.py" in out
    assert "docs/readme.md" in out


def test_churn_since_flag(make_repo, capsys):
    assert main(["churn", str(make_repo()), "--since", "2026-09-03"]) == 0

    out = capsys.readouterr().out
    assert "docs/readme.md" in out  # committed that day
    assert "src/core.py" in out  # touched that day too


def test_hotspots_text_output(make_repo, capsys):
    assert main(["hotspots", str(make_repo()), "-n", "1"]) == 0

    out = capsys.readouterr().out
    assert "src/core.py" in out  # highest churn x size


def test_bus_factor_text_output(make_repo, capsys):
    assert main(["bus-factor", str(make_repo()), "-n", "1"]) == 0

    out = capsys.readouterr().out
    assert "Ada Lovelace" in out  # main author of the most fragile file


def test_churn_json_output_is_json_safe(make_repo, capsys):
    assert main(["churn", str(make_repo()), "--json"]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "src/core.py"
    assert data[0]["last_touched"] == "2026-09-03"  # date, not datetime repr


def test_hotspots_json_output(make_repo, capsys):
    assert main(["hotspots", str(make_repo()), "--json"]) == 0

    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "src/core.py"
    assert data[0]["score"] == data[0]["churn"] * data[0]["size"]


def test_non_repository_exits_one(capsys):
    import tempfile

    with tempfile.TemporaryDirectory() as empty:
        assert main(["churn", empty]) == 1
        assert "repoheat:" in capsys.readouterr().err
