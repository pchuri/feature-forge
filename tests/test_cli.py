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

    def fake_fetch(store, app_ref, count, country, lang):
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


def test_fetch_command_passes_lang(tmp_path, monkeypatch) -> None:
    out = tmp_path / "out.csv"
    seen: dict[str, str] = {}

    def fake_fetch(store, app_ref, count, country, lang):
        seen["lang"] = lang
        seen["country"] = country
        match = AppMatch("jp.example", "Example App", Store.GOOGLE_PLAY)
        return [Review(rating=1, body="通知が全く来なくなりました")], match

    monkeypatch.setattr(cli, "fetch_reviews", fake_fetch)

    result = runner.invoke(
        app,
        ["fetch", "google-play", "Example", "--country", "jp", "--lang", "ja", "-o", str(out)],
    )
    assert result.exit_code == 0
    assert seen == {"lang": "ja", "country": "jp"}


def test_analyze_command_passes_model(tmp_path, monkeypatch) -> None:
    csv_path = tmp_path / "r.csv"
    csv_path.write_text(
        "rating,body\n1,Way too many ads in this app\n5,All good here thanks\n",
        encoding="utf-8",
    )

    constructed: list[str] = []

    class FakeEmbedder:
        pass

    def fake_make_embedder(spec: str) -> FakeEmbedder:
        constructed.append(spec)
        return FakeEmbedder()

    def fake_analyze(reviews, idea, n_clusters, embedder):
        assert isinstance(embedder, FakeEmbedder)
        from feature_forge.analysis import build_summary
        from feature_forge.models import AnalysisReport

        return AnalysisReport(idea=idea, summary=build_summary(reviews), clusters=[])

    monkeypatch.setattr(cli, "make_embedder", fake_make_embedder)
    monkeypatch.setattr(cli, "analyze", fake_analyze)

    result = runner.invoke(
        app,
        [
            "analyze",
            str(csv_path),
            "--idea",
            "X",
            "--model",
            "paraphrase-multilingual-MiniLM-L12-v2",
            "-o",
            str(tmp_path / "report.md"),
        ],
    )
    assert result.exit_code == 0
    assert constructed == ["paraphrase-multilingual-MiniLM-L12-v2"]


def test_analyze_command_reports_embedding_setup_errors(tmp_path, monkeypatch) -> None:
    csv_path = tmp_path / "r.csv"
    csv_path.write_text(
        "rating,body\n1,Way too many ads in this app\n5,All good here thanks\n",
        encoding="utf-8",
    )

    def failing_make_embedder(spec: str):
        raise cli.EmbeddingError("OPENAI_API_KEY is not set.")

    monkeypatch.setattr(cli, "make_embedder", failing_make_embedder)

    result = runner.invoke(
        app,
        ["analyze", str(csv_path), "-i", "X", "--model", "openai:", "-o", str(tmp_path / "r.md")],
    )
    assert result.exit_code == 1
    assert "Embedding setup failed" in result.output
