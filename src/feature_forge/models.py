"""Pydantic data models shared across the Feature Forge pipeline."""

from __future__ import annotations

import datetime as _dt

from pydantic import BaseModel, Field, field_validator


class Review(BaseModel):
    """A single user review loaded from an input file."""

    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5.")
    body: str = Field(..., description="Main review text.")
    title: str | None = Field(default=None, description="Optional review title.")
    date: _dt.date | None = Field(default=None, description="Optional ISO review date.")
    app_name: str | None = Field(default=None, description="Optional source app name.")
    locale: str | None = Field(default=None, description="Optional locale, e.g. en-US.")

    @field_validator("title", "body", "app_name", "locale", mode="before")
    @classmethod
    def _strip_strings(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @property
    def text(self) -> str:
        """Combined title + body used for embedding and keyword extraction."""
        if self.title:
            return f"{self.title}. {self.body}"
        return self.body

    @property
    def is_negative(self) -> bool:
        """A review is treated as negative when its rating is 1 or 2 stars."""
        return self.rating <= 2


class ClusterResult(BaseModel):
    """A cluster of similar reviews plus its derived opportunity metrics."""

    cluster_id: int
    label: str
    size: int
    avg_rating: float
    negative_ratio: float
    opportunity_score: float
    keywords: list[str] = Field(default_factory=list)
    representative_reviews: list[str] = Field(default_factory=list)


class DatasetSummary(BaseModel):
    """Aggregate statistics for the cleaned review set."""

    total_reviews: int
    average_rating: float
    negative_count: int
    date_min: _dt.date | None = None
    date_max: _dt.date | None = None


class AnalysisReport(BaseModel):
    """The full result of an analysis run, ready to render to Markdown."""

    idea: str
    summary: DatasetSummary
    clusters: list[ClusterResult]
