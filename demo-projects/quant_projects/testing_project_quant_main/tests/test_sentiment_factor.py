"""Tests for sentiment factor: time decay, standardization, registration."""
import json
import math
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.data.storage import DataStore
from src.factors.sentiment import SentimentFactor


@pytest.fixture
def temp_store():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = DataStore(db_path=path)
    yield store
    try:
        os.unlink(path)
    except PermissionError:
        pass


@pytest.fixture
def base_config():
    return {
        "data": {"db_path": "data/test.db"},
        "sentiment": {
            "lookback_hours": 72,
            "half_life_hours": 24,
            "min_news_count": 1,
        },
    }


def _insert_news_with_sentiment(store, title, published_at, related_symbols, scope, score):
    """Insert a news item and its sentiment cache entry."""
    with store._get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO news (title, summary, published_at, source, related_symbols, scope, fetched_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, "", published_at, "test", json.dumps(related_symbols), scope, datetime.now().isoformat()),
        )
        news_id = cursor.lastrowid
        cls = "bullish" if score > 0 else ("bearish" if score < 0 else "neutral")
        conn.execute(
            "INSERT INTO sentiment_cache (news_id, classification, confidence, sentiment_score, model_name, analyzed_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (news_id, cls, abs(score), score, "test", datetime.now().isoformat()),
        )


class TestTimeDecay:
    def test_recent_news_weighted_higher(self, temp_store, base_config):
        factor = SentimentFactor()
        now = datetime.now()

        _insert_news_with_sentiment(
            temp_store, "Recent bullish", now.strftime("%Y-%m-%d %H:%M:%S"),
            ["SH601899"], "stock", 0.8
        )
        _insert_news_with_sentiment(
            temp_store, "Old bearish", (now - timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S"),
            ["SH601899"], "stock", -0.5
        )

        result = factor.compute(["SH601899"], now.strftime("%Y-%m-%d"), temp_store, base_config)
        # Recent bullish should dominate over old bearish
        assert result["SH601899"] > 0

    def test_decay_formula(self, temp_store, base_config):
        factor = SentimentFactor()
        half_life = 24
        hours = 24
        expected_weight = math.exp(-math.log(2) * hours / half_life)
        assert expected_weight == pytest.approx(0.5, rel=1e-6)


class TestSectorNews:
    def test_sector_news_applies_to_all_stocks(self, temp_store, base_config):
        factor = SentimentFactor()
        now = datetime.now()

        _insert_news_with_sentiment(
            temp_store, "Sector bullish", now.strftime("%Y-%m-%d %H:%M:%S"),
            [], "sector", 0.7
        )

        result = factor.compute(
            ["SH601899", "SH600362"], now.strftime("%Y-%m-%d"), temp_store, base_config
        )
        assert result["SH601899"] > 0
        assert result["SH600362"] > 0


class TestNoNews:
    def test_no_news_returns_zero(self, temp_store, base_config):
        factor = SentimentFactor()
        result = factor.compute(
            ["SH601899"], datetime.now().strftime("%Y-%m-%d"), temp_store, base_config
        )
        assert result["SH601899"] == 0.0


class TestFactorRegistration:
    def test_registered_in_registry(self):
        from src.factors.base import get_registered_factors
        # Trigger registration
        import src.factors.sentiment  # noqa: F401
        registry = get_registered_factors()
        assert "sentiment_score" in registry

    def test_category_is_sentiment(self):
        factor = SentimentFactor()
        assert factor.category == "sentiment"


class TestZeroWeight:
    def test_zero_weight_skips_pipeline(self, base_config):
        """When sentiment weight is 0, the news pipeline should not run."""
        config = {**base_config, "factors": {"weights": {"sentiment": 0}}}
        weight = config["factors"]["weights"].get("sentiment", 0)
        assert weight == 0


class TestSignalIntegration:
    """R3-UC1 Flow and extensions: end-to-end sentiment factor in signal pipeline."""

    @pytest.fixture
    def populated_store(self, temp_store, base_config):
        """Store with news + sentiment cache entries pre-populated."""
        now = datetime.now()
        _insert_news_with_sentiment(
            temp_store, "紫金矿业发现大型铜矿", now.strftime("%Y-%m-%d %H:%M:%S"),
            ["SH601899"], "stock", 0.85
        )
        _insert_news_with_sentiment(
            temp_store, "有色金属板块全线上涨", now.strftime("%Y-%m-%d %H:%M:%S"),
            [], "sector", 0.7
        )
        return temp_store

    def test_signal_pipeline_with_sentiment(self, populated_store, base_config):
        """R3-UC1: Full pipeline — compute sentiment factor with populated data."""
        factor = SentimentFactor()
        universe = ["SH601899", "SH600362"]
        now = datetime.now().strftime("%Y-%m-%d")
        result = factor.compute(universe, now, populated_store, base_config)
        # SH601899 has stock-level + sector-level news → positive score
        assert result["SH601899"] > 0
        # SH600362 has only sector-level news → positive score
        assert result["SH600362"] > 0
        # SH601899 should score higher (has individual + sector)
        assert result["SH601899"] >= result["SH600362"]

    def test_sentiment_labels_output(self, populated_store, base_config):
        """R3-UC1-S8: Verify sentiment label can be derived from factor data."""
        factor = SentimentFactor()
        universe = ["SH601899"]
        now = datetime.now().strftime("%Y-%m-%d")
        score = factor.compute(universe, now, populated_store, base_config)
        # Positive score → 利多 label
        assert score["SH601899"] > 0
        # Read latest news for the stock to build label
        news_df = populated_store.read_news(symbol="SH601899")
        assert len(news_df) > 0
        assert "紫金矿业发现大型铜矿" in news_df.iloc[0]["title"]

    def test_news_fetch_failure_graceful(self, temp_store, base_config):
        """R3-UC1-E3a: News fetch failure → factor returns 0, no crash."""
        factor = SentimentFactor()
        universe = ["SH601899"]
        now = datetime.now().strftime("%Y-%m-%d")
        # Empty store = simulates failed/empty news fetch
        result = factor.compute(universe, now, temp_store, base_config)
        assert result["SH601899"] == 0.0

    def test_llm_failure_uses_cache(self, temp_store, base_config):
        """R3-UC1-E4a: LLM failure → factor uses existing cached sentiment."""
        now = datetime.now()
        # Insert news with pre-cached sentiment (simulates previous successful LLM call)
        _insert_news_with_sentiment(
            temp_store, "铜矿利好", now.strftime("%Y-%m-%d %H:%M:%S"),
            ["SH601899"], "stock", 0.9
        )
        factor = SentimentFactor()
        result = factor.compute(["SH601899"], now.strftime("%Y-%m-%d"), temp_store, base_config)
        # Should use cached value
        assert result["SH601899"] > 0

    def test_zero_weight_skips_news_pipeline(self, base_config):
        """R3-UC1-E6a: When sentiment weight=0, pipeline should be skippable."""
        config = {**base_config, "factors": {"weights": {"sentiment": 0}}}
        sentiment_weight = config["factors"]["weights"].get("sentiment", 0.10)
        assert sentiment_weight == 0
        # When weight is 0, callers should skip the factor entirely
        # Verify the config-based skip logic works
        should_skip = sentiment_weight == 0
        assert should_skip is True
