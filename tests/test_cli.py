"""Tests for CLI argument routing/validation (no network, no model download)."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from feature_forge import cli
from feature_forge.cli import app
from feature_forge.fetchers import AppMatch, Store
from feature_forge.models import Review

runner = CliRunner()


def test_analyze_requires_a_source() -> None:
    result = runner.invoke(app, ["analyze", "--idea", "X"])
    assert result.exit_code == 2
    assert "Nothing to analyze" in result.output


def test_analyze_rejects_file_and_store_together(tmp_path: Path) -> None:
    csv_path = tmp_path / "r.csv"
    csv_path.write_text("rating,body\n5,All good here thanks\n", encoding="utf-8")
    result = runner.invoke(
        app,
        ["analyze", str(csv_path), "--idea", "X", "--store", "google-play", "--app", "W"],
    )
    assert result.exit_code == 2
    assert "not both" in result.output


def test_analyze_store_requires_app() -> None:
    result = runner.invoke(app, ["analyze", "--idea", "X", "--store", "google-play"])
    assert result.exit_code == 2
    assert "--store requires --app" in result.output


def test_fetch_command_saves(tmp_path, monkeypatch) -> None:
    out = tmp_path / "out.csv"

    def fake_fetch(store, app_ref, count, country):
        assert store is Store.GOOGLE_PLAY
        match = AppMatch("com.example", "Example App", Store.GOOGLE_PLAY)
        reviews = [Review(rating=2, body="This app is far too slow lately")]
        return reviews, match

    monkeypatch.setattr(cli, "fetch_reviews", fake_fetch)

    result = runner.invoke(
        app, ["fetch", "google-play", "Example", "--count", "5", "-o", str(out)]
    )
    assert result.exit_code == 0
    assert out.exists()
    assert "Example App" in result.output
    assert "Saved 1 review(s)" in result.output
